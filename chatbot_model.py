# ./chatbot_model.py

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from chatbot_config import CONFIG
from time import time

class ChatbotByGemini:
    # api 모델 호출
    def __init__(self):
        load_dotenv(dotenv_path="./chatbot.env")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_key:
            raise ValueError("API KEY 미설정 : chatbot.env에 gemini api key를 등록하십시오.")
        self.client = genai.Client(api_key=self.gemini_key)

    def extract_context(docs = None):
        '''
        추후 개발 예정 : 참고 자료 정보 제공 기능
        '''
        return None

    # 응답 생성
    def answer(self, user_q, context= None):
        if not self.client:
            raise ValueError("API client 초기화 실패")

        try:
            user_prompt = f'''
            [사용자 질문]
            {user_q}

            [참고 자료]
            {context}

            위 내용을 바탕으로 신뢰할수 있는 답변을 해줘.
            '''
            start_time = time()
            response = self.client.models.generate_content(
                model= CONFIG.GENERATION_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=CONFIG.PROMPT,
                    temperature=CONFIG.TEMPURATURE
                ),
                contents=user_prompt
            )

            print(f"{response.text}\n\n 소요 시간 : {time() - start_time:.2f}")

        except Exception as e:
            return f"응답 생성 중 에러 발생 \n{str(e)}"
        
