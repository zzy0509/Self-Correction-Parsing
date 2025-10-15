import openai


openai.api_key =  ""
openai.api_base= ""

def replace(prompt):
    while True:
        try:
            message = [{'role':'user','content':prompt}]
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages = message,
                max_tokens=2000,
                temperature=0,
                stop=None)
            generated_text = response.choices[0].message.content
            break
        except:
            pass

    return generated_text


prompt = open(r"prompt.txt","r",encoding="utf-8").read()
answer = open(r"result.txt","w",encoding="utf-8")
test = open(r"test.txt","r",encoding="utf-8").read().split('\n')



for i in test:
    answer.write('TREE'+'\n')
    a = replace(prompt+i+'\nOutput:')
    answer.write(a+'\n\n')
