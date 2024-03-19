from datasets import Dataset, load_dataset
from enum import Enum
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments


class SupportedModel(Enum):
    LLAMA = 'meta-llama/Llama-2-7b-hf', 'Llama 2'
    PHI_2 = 'microsoft/phi-2', 'Phi-2'
    MISTRAL = 'mistralai/Mistral-7B-v0.1', 'Mistral'

    def __init__(self, model_name: str, display_name: str) -> None:
        super().__init__()
        self._model_name = model_name
        self._display_name = display_name

    @property
    def directory_name(self) -> str:
        return self._model_name.split('/')[-1]

    @property
    def display_name(self) -> str:
        return self._display_name

    def get_trainer(self, dataset: Dataset, training_args: TrainingArguments | None = None) -> Trainer:
        if self is SupportedModel.PHI_2:
            return Trainer(model=AutoModelForCausalLM.from_pretrained(self._model_name,
                                                                      trust_remote_code=True),
                           tokenizer=AutoTokenizer.from_pretrained(self._model_name,
                                                                   trust_remote_code=True),
                           train_dataset=dataset, args=training_args)  # type: ignore
        return Trainer(model=AutoModelForCausalLM.from_pretrained(self._model_name),
                       tokenizer=AutoTokenizer.from_pretrained(
                           self._model_name),
                       train_dataset=dataset, args=training_args)  # type: ignore

    @classmethod
    def from_name(cls, name: str) -> 'SupportedModel':
        for model in cls:
            if model.directory_name == name.split('/')[-1]:
                return model
        raise ValueError(f'Not a supported model: {name}')


class LLM:

    def __init__(self, path: Path, model: SupportedModel) -> None:
        self._path = path
        self._model = model

    @property
    def model(self) -> str:
        return self._model.display_name

    @classmethod
    def from_pretrained(cls, path: Path) -> 'LLM':
        return cls(path, SupportedModel.from_name(path.name))