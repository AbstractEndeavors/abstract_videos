from .routes import *
logger =get_logFile() 
nlp = spacy.load("en_core_web_sm")
def get_content_length(text):
    for each in ['into a ']:
        if each in text:
            text = text.split(each)[1]
            break
    for each in [' word']:
        if each in text:
            text = text.split(each)[0]
            break
    numbers = []
    for each in text.split('-'):
        numbers.append('')
        for char in each:
            char = str(char)
            if char in list('1234567890'):
                numbers[-1]+=char
    for i,number in enumerate(numbers):
        if number:
            numbers[i]=int(number)*10
    return numbers
    
def refine_with_gpt(full_text: str,task=None) -> str:
    prompt = generate_with_bigbird(full_text,task=task)
    lengths = get_content_length(full_text)
    max_length=200
    min_length=100
    if lengths:
        max_l = lengths[-1]
        if max_l:   
            max_length = int(max_l)
        min_l = lengths[0]
        if min_l: 
            min_length = int(min_l)
    out = generator(prompt, min_length=min_length,max_length=max_length, num_return_sequences=1)[0]["generated_text"]
    return out.strip()
def generate_with_bigbird(text: str, task: str = "title", model_dir: str = "allenai/led-base-16384") -> str:
    try:
        tokenizer = LEDTokenizer.from_pretrained(model_dir)
        model = LEDForConditionalGeneration.from_pretrained(model_dir)
        prompt = (
            f"Generate a concise, SEO-optimized {task} for the following content: {text[:1000]}"
            if task in ["title", "caption", "description"]
            else f"Summarize the following content into a 100-150 word SEO-optimized abstract: {text[:4000]}"
        )
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            inputs["input_ids"],
            max_length=200 if task in ["title", "caption"] else 300,
            num_beams=5,
            early_stopping=True
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error in BigBird processing: {e}")
        return ""
