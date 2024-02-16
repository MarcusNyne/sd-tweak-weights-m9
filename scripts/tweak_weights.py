import os
import copy
from datetime import datetime

from modules.processing import fix_seed
import modules.scripts as scripts
import gradio as gr

from modules import images
from modules.processing import Processed, process_images
from modules.shared import state

from scripts.m_prompt2 import *

class Script(scripts.Script):
    def __init__(self):
        self.__inside = False
        pass

    def title(self):
        return "Tweak Weights [M9]"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):

        with gr.Group(elem_id="m9-tweak-weights-accordion-group"):
            with gr.Accordion("Tweak Weights [M9]", open=False, elem_id="m9-tweak-weights-accordion"):
                is_enabled = gr.Checkbox(
                    label="Tweak Weights enabled",
                    value=False,
                    interactive=True,
                    elem_id="m9-tweak-weights-enabled",
                )

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
                                chk_variation_folders = gr.Checkbox(label="Create variation folders", infox="Causes an image subfolder to be created for a variation", value=False, elem_id=self.elem_id("chk_variation_folders"))

        return [is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, markdown]

    def process(self, p, is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, markdown):

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
                        if p.prompt==p.hr_prompt:
                            copy_p.hr_prompt = ''
                        if chk_variation_folders is True:
                            copy_p.outpath_samples = self.__calc_outpath(var_ix)
                        processed = process_images(copy_p)

                        self._processed_images += processed.images
                        self._processed_all_prompts += processed.all_prompts
                        self._processed_infotexts += processed.infotexts

                except:
                    print("Tweak Weights [M9]: Exception during processing")
 
            self.__inside = False
            self.__print_variation_header(self._cnt_variations-1)

    def __if_zero(self, inValue):
        return None if (inValue is None or inValue==0.0) else inValue
    def __if_zint(self, inValue):
        return None if (inValue is None or inValue==0.0) else int(inValue)

    def __print_variation_header(self, in_iteration):
        print(f"Variation {in_iteration+1} of {self._cnt_variations} [{self._outpath_root}].\n")

    def __calc_outpath(self, in_iteration):
        return os.path.join (self._original_outpath, f"{self._outpath_root}-{in_iteration+1:02d}")

    def __generate_prompt(self, prompt_keywords, weight_range, weight_max, lora_weight_range):
        weight_range=self.__if_zero(weight_range)
        lora_weight_range=self.__if_zero(lora_weight_range)
        prompt = mPrompt2(inSeed=None, inPrompt=self._original_prompt)
        prompt.TweakWeights(prompt_keywords, weight_range, lora_weight_range, weight_max)
        new_prompt = prompt.Generate()
        return new_prompt

    def before_process(self, p, is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, markdown):

        if self.__inside or not is_enabled:
            return

        fix_seed(p)
        p.do_not_save_grid = True
        self._cnt_variations = int(cnt_variations)
        self._outpath_root = datetime.now().strftime("%y%m%d-%H%M")
        self._original_seed = p.seed
        self._original_prompt = p.prompt
        self._original_outpath = p.outpath_samples
        self._processed_images = []
        self._processed_all_prompts = []
        self._processed_infotexts = []
        state.job_count = self._cnt_variations * p.n_iter

        if chk_variation_folders is True:
            p.outpath_samples = self.__calc_outpath(self._cnt_variations-1)
        p.prompt = self.__generate_prompt(prompt_keywords, weight_range, weight_max, lora_weight_range)
        pass

    def postprocess(self, p, processed, is_enabled, prompt_keywords, chk_variation_folders, cnt_variations, weight_range, weight_max, lora_weight_range, markdown):
        if self.__inside or not is_enabled:
            return

        self._processed_images += processed.images
        self._processed_all_prompts += processed.all_prompts
        self._processed_infotexts += processed.infotexts

        processed.images = self._processed_images
        processed.all_prompts = self._processed_all_prompts
        processed.infotexts = self._processed_infotexts
