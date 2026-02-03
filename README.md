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
- Vincent Yang at [wenjiey012@gmail.com](mailto:wenjiey012@gmail.com).

## About

<div align="center">

In this paper, we selected 30 projects based on their star count and commit activity for an
observational analysis of open-source projects from different communities. Our observational
analysis focuses on statistically examining code modifications, contributor behaviors, and changes in statement types to reveal patterns in code cleanliness evolution. 

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

The primary contributions of this work encompass:

* ✨ Conducting the first large-scale empirical study to assess evolving trends of open-source projects
from the code cleanliness perspective. Our analysis of the open-source projects from Apache,
Google, and Spring, involving 84,268,300 lines, 4,356,940 functions, and 197,461 file pairs, revealed
that most of the code within these projects has changed within standard limits, aligning with
the clean code standard.
* ✨ Through an examination of committer information related to positive and negative code changes,
we discovered a higher frequency of positive changes during manual code reviews compared to
automatic additions to the codebase, highlighting the significant role of human developers in
code review responsibilities. 
* ✨ Our analysis of the word clouds from code changes shows that refactoring is key to improving
code cleanliness, aligning with principles proposed by Martin. However, not all contributors’
refactoring efforts effectively align with clean code standards. Common terms like "support," "im-
prove," and "enhance" often appear in commit messages but can sometimes introduce complexity,
misaligning with clean code goals.
* ✨ Our analysis results guide the targeted code review by highlighting the different degrees of
emphasis on modified statement types within each referenced indicator of clean code.

`ECC-Dataset`: Given that Google, Apache, and Spring-projects have been widely
referenced in previous studies, our focus lies on open-source projects from these three
communities. For project selection, we utilize GitHub’s advanced search 15 to filter projects by
language and organization name. From this pool, we further narrow the selection based on the
number of stars and commits in recent years, as shown in figure of workflow, ultimately selecting the top 10
projects from each organization. These well-known open-source projects have also been widely
studied in the literature. Our analysis covers code master commits made between
January 1, 2022, and December 15, 2024. We utilized ASTs to establish mapping relationships
between files and functions before and after code changes. This resulted in a dataset comprising
197,461 pairs of files (before vs. after), 4,356,94 functions, and 84,268,300 code lines.

## 🚀 Getting Started 

We provide all the source code implemented to build ECC and evaluate LLMs on CODAL-Bench.

> [!IMPORTANT]
> 
> We are currently working on instructions to:
> 1. Build ECC or extend the dataset
> 2. Tune your own SFT and DPO LLMs
> 3. Evaluate LLMs on CODAL-Bench

## Datasets
- 🤗 **ECC-dataset**: [https://huggingface.co/datasets/coseal/ECC_binarized](https://huggingface.co/datasets/coseal/ECC_binarized)

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