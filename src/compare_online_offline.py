import os
from pathlib import Path
from config import load_config
from agent_advanced import AdvancedAgent

def main():
    root = Path(__file__).resolve().parent.parent
    config = load_config(root)
    
    print("=== So sánh Offline vs Online ===")
    
    # 1. Chạy Offline
    print("\n[1] CHẠY OFFLINE (Deterministic Mock)")
    offline_advanced = AdvancedAgent(config=config, force_offline=True)
    res_off = offline_advanced.reply("user_compare", "thread_off", "Chào bạn, tôi tên là Minh. Tôi đang làm kĩ sư AI.")
    print(f"User: Chào bạn, tôi tên là Minh. Tôi đang làm kĩ sư AI.")
    print(f"Offline Agent: {res_off['response']}")
    
    res_off_2 = offline_advanced.reply("user_compare", "thread_off", "Nhắc lại xem tôi tên gì và làm nghề gì?")
    print(f"User: Nhắc lại xem tôi tên gì và làm nghề gì?")
    print(f"Offline Agent: {res_off_2['response']}")
    print(f"(Tokens Processed: {res_off_2['prompt_tokens_processed']})")
    
    # 2. Chạy Online
    print("\n[2] CHẠY ONLINE (Live API)")
    if config.model.provider in ["custom", "offline-mock"] and not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("=> CHÚ Ý: Chưa thiết lập API Key thật (OPENAI_API_KEY hoặc GEMINI_API_KEY) trong file .env.")
        print("=> Vui lòng cấu hình file .env (vd: LLM_PROVIDER=openai, OPENAI_API_KEY=...) để thử nghiệm Online.")
        return
        
    try:
        online_advanced = AdvancedAgent(config=config, force_offline=False)
        if not online_advanced.langchain_agent:
            print("=> Không thể khởi tạo Online Agent (thiếu key hoặc thư viện).")
            return
            
        res_on = online_advanced.reply("user_compare_on", "thread_on", "Chào bạn, tôi tên là Tuấn. Tôi đang làm Frontend Dev.")
        print(f"User: Chào bạn, tôi tên là Tuấn. Tôi đang làm Frontend Dev.")
        print(f"Online Agent: {res_on['response']}")
        
        res_on_2 = online_advanced.reply("user_compare_on", "thread_on", "Nhắc lại xem tôi tên gì và làm nghề gì?")
        print(f"User: Nhắc lại xem tôi tên gì và làm nghề gì?")
        print(f"Online Agent: {res_on_2['response']}")
        print(f"(Tokens Processed: {res_on_2['prompt_tokens_processed']})")
        
    except Exception as e:
        print(f"Lỗi khi gọi API thực: {e}")
        
    print("\n=== Tổng kết ===")
    print("- Offline: Nhanh, không tốn phí, nhưng câu trả lời rập khuôn (cứng nhắc).")
    print("- Online: Phản hồi tự nhiên, linh hoạt, nhưng sẽ tốn phí thật dựa trên lượng Prompt Tokens Processed.")

if __name__ == "__main__":
    main()
