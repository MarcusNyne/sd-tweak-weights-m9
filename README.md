# Stable Diffusion: Tweak Weights [m9]

A custom extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

This extension modifies prompt weights in order to find a better version of an existing prompt.  Only prompts containing specified keywords are modified.

*Not intended to be used while Scramble Prompts [m9] is in use*

## Details

Only prompts that match one of the specified keywords will be modified.

  * **Prompt Keywords**: Keywords to match
    * Comma delimited
    * Not case sensitive
   * **Weight Range**: The maximum amount to modify the weight in either direction.
     * If a change would take the weight below zero, the weight will be left as is
     * Applied to non-Lora prompts
   * **Max Weight**: Maximum final weight.
     * When a change will take the weight over the max, the change is not made
     * For example, if the weight is 1, the max is 1.2, and the change is +0.3, the weight will be left at 1
   * **Lora Weight Range**: The maximum amount to modify a Lora weight.
     * Applied to Loras

### Variant Generation

   * **Variations (count)**: The number of variations to produce
     * Each variation will generate (count * batch) images
   * **Create variation folders**: Create a new folder per variation
     * All images for a variation will be placed in the folder
     * Folders will be named YYMMDD-HHMM-NN, where NN is the variation number

### Help and Feedback

   * **Discord Server**
     * https://discord.gg/trMfHcTcsG

### m9 Prompts Catalog

   * **Scramble Prompts for Stable Diffusion**
     * Works with Automatic1111
     * Reorder, remove, modify weights of prompts
     * https://github.com/MarcusNyne/sd-scramble-prompts-m9

   * **Tweak Weights for Stable Diffusion**
     * Works with Automatic1111
     * Modify prompt weights using keywords
     * https://github.com/MarcusNyne/sd-tweak-weights-m9

   * **m9 Prompts for ComfyUI**
     * Works with ComfyUI
     * Includes nodes for Scramble Prompts and Tweak Weights
     * https://github.com/MarcusNyne/m9-prompts-comfyui

