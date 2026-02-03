# `Evolving Code Cleanliness (ECC): A Tools`
<div align="center">

## **Evolving Trends in Cleanliness of Open Source Projects**

</div>

<p align="center">
    <a target="_blank" href="https://arxiv.org/abs/2403.09032"><img src="https://img.shields.io/badge/ArXiV-2404.09032-a55fed.svg"></a>
    <a target="_blank" href="https://huggingface.co/datasets/coseal/ECC"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-ECC-%23ff8811.svg"></a>
    <a target="_blank" href="https://github.com/martin-wey/ECC/blob/main/LICENSE"><img src="https://img.shields.io/github/license/martin-wey/ECC
"></a>
</p>

<p align="center">
    <a href="#about">🤔 About</a> •
    <a href="#-getting-started">🚀 Getting Started</a> •
    <a href="#datasets">🤗 Datasets</a> •
    <a href="#-citation">📝 Citation</a>
</p>

> [!NOTE]
>
> [02-03-2026] 🔥 We release the first version of ECC and datasets.

**Contact:** If you have any inquiries or want to raise an issue, please feel free to contact:
- Vicent Yang at [wenjiey012@gmail.com](mailto:wenjiey012@gmail.com).

## About

<div align="center">

![Overview of ECC](assets/framework.png)

_Overview of ECC workflow (see [Section II of our paper](https://arxiv.org/abs/2403.09032) for more details)._
</div>

> Our investigation addresses the following research questions:
> 
> RQ-1. Do open-source projects consistently adapt to cleaner modifications, and which met-
rics are predominantly emphasized by maintainers during the upkeep of these projects?
>
> This question explores the adherence of open-source project code to clean code standards, focus-
ing on eight perspectives: cyclomatic complexity (MethodCircles), LOCs in functions (Method-
Rows), LOCs in files (FileRows), code line lengths (LineChars), number of try-catch statements
(TryCatchNums), and the naming of classes, methods, and parameters.
> 
> RQ-2. To what degree are project maintainers committed to upholding clean code princi-
ples? Additionally, which specific categories of code modifications affect the code cleanli-
ness and necessitate particular scrutiny?
> 
> We categorize standard and non-standard modifica-
tions into positive and negative changes for this question, examining commit information and
generating word clouds.
> RQ-3. How significantly do alterations in code statements affect overall code cleanliness
when striving to write clean code? Moreover, regarding different metrics used to measure
clean code, which types of statement-level changes should be given priority for careful
consideration and possible revision?
> 
> In this question, we use the ASTs to analyze statement types and guide developers in making effective code modifications.
Our work features two main contributions: `ECC` and `ECC-Dataset`, a code repo and dataset for evolving trends in cleanliness of Open Source Projects.

`ECC` is a preference dataset of complex coding instructions to align LLMs to coding preferences. 
It has an analogous construction procedure to [UltraFeedback](https://github.com/OpenBMB/UltraFeedback), featuring:

* ✨ **Complex instructions**: ECC is based on a 10k subset of [MagiCoder Evol-Instruct](https://huggingface.co/datasets/ise-uiuc/Magicoder-Evol-Instruct-110K) comprising open domain complex coding instructions.
* ✨ **Coding preferences**: ECC includes 5 coding preferences, which are crucial to evaluate the broader capabilities of LLMs: **instruction-following**, **code explanation**, **code complexity and efficiency**, **code readability**, and **coding style**.
* ✨ **Large pool of LLMs**: We use a large pool of 14 LLMs from 8 model families to generate responses to the 10k instructions to consider diverse writing and coding styles.
* ✨ **LLM-as-a-judge and AI feedback**: We use GPT-3.5 as a judge for evaluating LLM responses, which annotates each response with both numerical and textual feedback. The AI feedback data can be leveraged for various applications, including model alignment through RLAIF, tuning a critic LLM, and more.

`CODAL-Bench` is a benchmark of 500 coding problems (_100 per coding preference_). We use LLM-as-a-judge with reference-guided single-answer grading using GPT-3.5 or GPT-4 to evaluate LLM alignment. 
The approach enables the judge LLM to provide consistent ratings and evaluate each LLM individually (similar to [MT-Bench](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge)). 

## 🚀 Getting Started 

We provide all the source code implemented to build ECC and evaluate LLMs on CODAL-Bench.

> [!IMPORTANT]
> 
> We are currently working on instructions to:
> 1. Build ECC or extend the dataset
> 2. Tune your own SFT and DPO LLMs
> 3. Evaluate LLMs on CODAL-Bench

## Models

| Model                             | Checkpoint                                                                      | Size | CODAL-Bench GPT-3.5<br/>(G-3.5, G-4) | CODAL-Bench GPT-4 <br/>(G-4) | HumanEval+<br/>(k=1, k=10) | License                                      |
|:----------------------------------|:--------------------------------------------------------------------------------|:----:|:------------------------------------:|:----------------------------:|:--------------------------:|:---------------------------------------------|
| **CodeLlama-7B-Instruct**         | 🤗 [HF Link](https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf)         | `7B` |             6.00 / 5.46              |             4.72             |        37.9 / 60.4         | [Llama2](https://ai.meta.com/llama/license/) |
| **CodeLlama-7B-Instruct-SFT**     | 🤗 [HF Link](https://huggingface.co/coseal/CodeLlama-7B-Instruct-sft-qlora)     | `7B` |             6.51 / 5.83              |             5.84             |    **51.2** / **82.9**     | [Llama2](https://ai.meta.com/llama/license/) |
| **CodeLlama-7B-Instruct-DPO**     | 🤗 [HF Link](https://huggingface.co/coseal/CodeLlama-7B-Instruct-dpo-qlora)     | `7B` |             7.15 / 6.79              |             5.08             |        42.3 / 80.5         | [Llama2](https://ai.meta.com/llama/license/) |
| **CodeLlama-7B-Instruct-SFT+DPO** | 🤗 [HF Link](https://huggingface.co/coseal/CodeLlama-7B-Instruct-sft-dpo-qlora) | `7B` |         **7.36** / **7.08**          |           **5.85**           |        43.1 / 75.6         | [Llama2](https://ai.meta.com/llama/license/) |

## Datasets and Benchmark
- 🤗 **ECC**: [https://huggingface.co/datasets/coseal/ECC](https://huggingface.co/datasets/coseal/ECC)
- 🤗 **ECC binarized**: [https://huggingface.co/datasets/coseal/ECC_binarized](https://huggingface.co/datasets/coseal/ECC_binarized)
- 🤗 **CODAL-Bench**: [https://huggingface.co/datasets/coseal/codal-bench](https://huggingface.co/datasets/coseal/codal-bench)
- 🤗 **Magicoder-Evol-Instruct-110K-sft**: [https://huggingface.co/datasets/coseal/Magicoder-Evol-Instruct-110K-sft](https://huggingface.co/datasets/coseal/Magicoder-Evol-Instruct-110K-sft)

## 📝 Citation
```bibtex
@misc{weyssow2024ECC,
  title={ECC: An LLM-as-a-Judge Dataset for Aligning Large Language Models to Coding Preferences}, 
  author={Martin Weyssow and Aton Kamanda and Houari Sahraoui},
  year={2024},
  eprint={2403.09032},
  archivePrefix={arXiv},
  primaryClass={cs.SE}
}
```