# ./chatbot_main.py

import logging
from chatbot.service import ChatbotByGemini

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Main")

def main():
    try:
        model = ChatbotByGemini()
        logger.info("Chatbot system is ready.")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")
        return

    print("\n🚀 아주대 국제학생 지원 챗봇이 실행되었습니다. (종료: q 또는 c)")
    
    while True:
        try:
            user_input = input("\n질문 [escape word = q / c]: ").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["q", "c"]:
                logger.info("User requested termination.")
                print("사용자가 종료 키워드를 입력했습니다. 프로그램을 종료합니다.")
                break

            # 1. 컨텍스트 추출 (RAG 검색)
            context = model.extract_context(user_input)
            
            # DEBUG 레벨일 때만 검색된 컨텍스트를 출력하도록 설정 가능
            logger.debug(f"Retrieved Context: {context}")

            # 2. 답변 생성
            response = model.answer(user_input, context)
            print(f"\n🤖 답변:\n{response}")
            
        except KeyboardInterrupt:
            logger.warning("Program interrupted by user (Ctrl+C).")
            print("\n사용자에 의해 종료되었습니다.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()