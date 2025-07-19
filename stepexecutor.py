import logging

# ...existing code...
    response = client.chat.completions.create(
        model="model-router",
        messages=messages,
    )
    model_name = getattr(response, 'model', None)
    if model_name:
        logging.info(f"StepExecutor used model: {model_name}")
        response2 = client.chat.completions.create(model="gpt-4.1", messages=messages)
        model_name = getattr(response2, 'model', None)
        if model_name:
            import logging
            logging.info(f"StepExecutor (response2) used model: {model_name}")
# ...existing code...