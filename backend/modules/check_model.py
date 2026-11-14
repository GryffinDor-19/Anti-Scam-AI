import google.generativeai as genai

# Điền API Key của bạn vào đây
genai.configure(api_key="API KEY cua bon m")

print("Danh sách các model AI mà API Key của bạn được phép gọi:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
