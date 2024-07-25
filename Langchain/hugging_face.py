from transformers import pipeline

FRASE = " The capital of ___ is Brasilia."

models = {
    'bert-base-uncased' : {'name':'bert-base-uncased',
                           'mask': '[MASK]',
                           },
    'distilbert-base-uncased': {'name':'distilbert-base-uncased',
                                'mask': '[MASK]',
                                },
    'xlm-roberta-base': {'name':'xlm-roberta-base',
                            'mask': '<mask>',
                            },
}

for key, value in models.items():
    print(f"Model: {key}")
    fill_mask = pipeline('fill-mask', model=value['name'],verbose=False)
    result = fill_mask(FRASE.replace('___', value['mask']))
    print(result[0])