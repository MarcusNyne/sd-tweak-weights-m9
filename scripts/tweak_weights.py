import os
import copy
from datetime import datetime

from modules.processing import fix_seed
import modules.scripts as scripts
import gradio as gr
from modules.shared import opts
if hasattr(opts, 'hypertile_enable_unet'):  # webui >= 1.7
    from modules.ui_components import InputAccordion
else:
    InputAccordion = None

from modules import images
from modules.processing import Processed, process_images
from modules.shared import state

from m9_tw_libs.m_prompt import *

class Script(scripts.Script):
    def __init__(self):
        self.__inside = False
        self._prompt = None

    def title(self):
        return "Tweak Weights [M9]"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):

        tab = 't2i'  if not is_img2img else 'i2i'
        m9_label = 'Tweak Weights [M9]'
        m9_accordian = "m9-tweak-weights-accordion"
        m9_enabled = "m9-tweak-weights-enabled"
        with (
            InputAccordion(False, label=m9_label, elem_id=f'{m9_accordian}-{tab}') if InputAccordion
            else gr.Accordion(m9_label, open=False, elem_id=f'{m9_accordian}-{tab}')
            as is_enabled
        ):
            if not InputAccordion:
                with gr.Row(variant='compact'):
                    is_enabled = gr.Checkbox(label='Enable Tweak Weights', value=False, interactive=True, elem_id=f'{m9_enabled}-{tab}')

            with gr.Group(visible=True):
                with gr.Row():
                    with gr.Column(scale=19):
                        with gr.Row():
                            markdown = gr.Markdown("Prompt weights containing the specified keywords will be modified.  The entire count/batch will be run against a prompt variation before running the next one.")
                        with gr.Row():
                            prompt_keywords = gr.Textbox(label="Prompt Keywords (,)", lines=1, elem_id=self.elem_id("prompt_keywords"))
                        with gr.Row():
                            weight_range = gr.Number(label="Weight Range (+/-) ", value=0.5, step=0.1, minimum=0, elem_id=self.elem_id("weight_range"))
                            weight_max = gr.Number(label="Max Weight ", value=1.9, step=0.1, minimum=0, elem_id=self.elem_id("weight_max"))
                            lora_weight_range = gr.Number(label="Lora Weight Range (+/-) ", value=0.2, minimum=0, step=0.1, elem_id=self.elem_id("lora_weight_range"))
                        with gr.Row():
                            cnt_variations = gr.Slider(label="Variations (count)", info="Number of variations to produce.  (count*batch) images are produced for each variation.", minimum=1, maximum=100, value=1, step=1, elem_id=self.elem_id("cnt_variations"))
                        with gr.Row():
                            chk_variation_folders = gr.Checkbox(label="Create variation folders", value=False, elem_id=self.elem_id("chk_variation_folders"))
                            chk_info_textfile = gr.Checkbox(label="Create info text file", value=False, elem_id=self.elem_id("chk_info_textfile"))

        return [is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, chk_info_textfile, markdown]

    def process(self, p, is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, chk_info_textfile, markdown):

        if not self.__inside and is_enabled:

            if self._cnt_variations>1:

                self.__inside = True

                try:
                    for var_ix in range (self._cnt_variations-1):
                        self.__print_variation_header(var_ix)

                        p.seed = self._original_seed

                        new_prompt = self.__generate_prompt(prompt_keywords, weight_range, weight_max, lora_weight_range)

                        copy_p = copy.copy(p)
                        copy_p.prompt = new_prompt
                        if hasattr(p, 'hr_prompt') and p.prompt==p.hr_prompt:
                            copy_p.hr_prompt = ''
                        if chk_variation_folders is True:
                            opts.data['directories_filename_pattern'] = self.__calc_dirpattern(chk_variation_folders, var_ix)

                        processed = process_images(copy_p)

                        self._processed_images += processed.images
                        self._processed_all_prompts += processed.all_prompts
                        self._processed_infotexts += processed.infotexts

                        if chk_info_textfile is True:
                            self.__write_info_file(var_ix, chk_variation_folders, processed.images[0].already_saved_as if len(processed.images)>0 else None)

                except:
                    print("Tweak Weights [M9]: Exception during processing")
 
            self.__inside = False
            self.__print_variation_header(self._cnt_variations-1)
            if chk_variation_folders is True:
                opts.data['directories_filename_pattern'] = self.__calc_dirpattern(chk_variation_folders, self._cnt_variations-1)

    def __if_zero(self, inValue):
        return None if (inValue is None or inValue==0.0) else inValue
    def __if_zint(self, inValue):
        return None if (inValue is None or inValue==0.0) else int(inValue)

    def __print_variation_header(self, in_iteration):
        print(f"Variation {in_iteration+1} of {self._cnt_variations} [{self._outpath_root}].\n")

    def __iter_folder(self, in_iteration):
        return f"{self._outpath_root}-{in_iteration+1:02d}"

    def __is_none(self, in_pattern):
        if type(in_pattern) is not str:
            return True
        in_pattern = in_pattern.lstrip().rstrip('\\ /').lower()
        return in_pattern == '' or in_pattern == '[none]'

    def __safe_join(self, in_path, in_folder):
        if in_path is None:
            return in_folder
        return os.path.join(in_path, in_folder)

    def __calc_dirpattern(self, chk_variation_folders, in_iteration):
        if chk_variation_folders is False:
            return self._original_dirpattern if self._original_dirpattern is not None else ''
        elif self.__is_none(self._original_dirpattern):
            return self.__iter_folder(in_iteration)
        return self.__safe_join(self._original_dirpattern, self.__iter_folder(in_iteration))
    
    def __write_info_file(self, in_iteration, chk_variation_folders, in_image_file):
        filepath = None
        try:
            if self._prompt and in_image_file:
                if chk_variation_folders is True:
                    filename = self.__iter_folder(in_iteration)+"-info.txt"
                else:
                    filename = os.path.basename(in_image_file)+"-info.txt"

                filepath = os.path.join(os.path.dirname(in_image_file), filename)
                self._prompt.SavePrompt(filepath, inLog=True)
        except:
            print(f"Failed to write info text file: {filepath}")

    def __generate_prompt(self, prompt_keywords, weight_range, weight_max, lora_weight_range):
        weight_range=self.__if_zero(weight_range)
        lora_weight_range=self.__if_zero(lora_weight_range)
        self._prompt = mPrompt(inSeed=None, inPrompt=self._original_prompt)
        self._prompt.TweakWeights(prompt_keywords, weight_range, lora_weight_range, weight_max)
        new_prompt = self._prompt.Generate()
        return new_prompt
    
    def before_process(self, p, is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, chk_info_textfile, markdown):

        if self.__inside or not is_enabled:
            return

        fix_seed(p)
        p.do_not_save_grid = True
        self._cnt_variations = int(cnt_variations)
        self._outpath_root = datetime.now().strftime("%y%m%d-%H%M")
        self._original_seed = p.seed
        self._original_prompt = p.prompt
        self._original_outpath = p.outpath_samples
        self._original_dirpattern = opts.data['directories_filename_pattern'] if 'directories_filename_pattern' in opts.data else None
        self._processed_images = []
        self._processed_all_prompts = []
        self._processed_infotexts = []
        state.job_count = self._cnt_variations * p.n_iter

        if chk_variation_folders is True:
            opts.data['directories_filename_pattern'] = self.__calc_dirpattern(chk_variation_folders, self._cnt_variations-1)
        p.prompt = self.__generate_prompt(prompt_keywords, weight_range, weight_max, lora_weight_range)
        self._lastprompt = self._prompt

    def postprocess(self, p, processed, is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, chk_info_textfile, markdown):
        if self.__inside or not is_enabled:
            return

        self._processed_images += processed.images
        self._processed_all_prompts += processed.all_prompts
        self._processed_infotexts += processed.infotexts

        if chk_info_textfile is True:
            self._prompt = self._lastprompt
            self.__write_info_file(self._cnt_variations-1, chk_variation_folders, processed.images[0].already_saved_as if len(processed.images)>0 else None)

        processed.images = self._processed_images
        processed.all_prompts = self._processed_all_prompts
        processed.infotexts = self._processed_infotexts

        if chk_variation_folders is True:
            if self._original_dirpattern is None:
                del opts.data['directories_filename_pattern']
            else:
                opts.data['directories_filename_pattern'] = self._original_dirpattern