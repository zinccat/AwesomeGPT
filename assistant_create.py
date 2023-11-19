from openai import OpenAI
from key import OPENAI_API_KEY
import time
from copy import deepcopy

client = OpenAI(api_key=OPENAI_API_KEY)

# we'll need to save a dict of assistant_id and file_id
file = client.files.create(
  file=open("llm.json", "rb"),
  purpose='assistants'
)
file_id = file.id
# print(file_id)

assistant = client.beta.assistants.create(
  instructions="You are an advanced AI researcher. When asked a question, search your knowledge to answer the question.",
  model="gpt-3.5-turbo-1106",
  tools=[{"type": "retrieval"}],
  file_ids=[file_id]
)
assistant_id = assistant.id
# print(assistant_id)

thread = client.beta.threads.create()
# print(thread.id)

while True:
    user_message = input("Input your question: ")
    thread_message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    run_id = run.id

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status not in ["queued", "in_progress"]:
            break
        time.sleep(1)
    print(run.status)
    if run.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        last_message = deepcopy(messages.data[0])
        for message_content in last_message.content:
            # Access the actual text content
            message_content = message_content.text
            annotations = message_content.annotations
            citations = []
            
            # Iterate over the annotations and add footnotes
            for index, annotation in enumerate(annotations):
                # Replace the text with a footnote
                message_content.value = message_content.value.replace(annotation.text, f' [{index}]')
            
                # Gather citations based on annotation attributes
                if (file_citation := getattr(annotation, 'file_citation', None)):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f'[{index}] {file_citation.quote}')
            message_content.value += '\n' + '\n'.join(citations)
        response = last_message.content[0].text.value
        print(response)

    if run.status == "failed":
        print(run.last_error)