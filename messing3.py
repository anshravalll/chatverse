import tiktoken

def token_count(query):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(query)
    return len(tokens)

count_tokens_of_this = input() 

print_it = token_count(count_tokens_of_this)

print(print_it)