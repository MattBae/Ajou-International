# ./chatbot_main.py

from chatbot_model import ChatbotByGemini

model = ChatbotByGemini()

def main():
    while True:
        user_input = str(input("질문 [escape word = q / c]: "))

        if user_input.lower() in ["q", "c"]:
            print("사용자가 escape word를 입력했습니다. 사용을 종료합니다.")
            break

        context = model.extract_context()
        response = model.answer(user_input, context)
        print(response)

if __name__ == "__main__":
    main()