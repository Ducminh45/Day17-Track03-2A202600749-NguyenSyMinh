import sys
from pathlib import Path
from agent_advanced import AdvancedAgent
from config import load_config

def main():
    print("=== Khởi động Advanced Agent (Interactive Mode) ===")
    config = load_config(Path(__file__).resolve().parent.parent)
    
    # Sử dụng chế độ Offline (Fake LLM) để minh họa cách extract memory nhanh chóng mà không cần API key
    agent = AdvancedAgent(config=config, force_offline=True)
    
    user_id = "interactive_user"
    thread_id = "interactive_thread"
    
    print(f"User ID: {user_id}")
    print("Gõ 'quit' hoặc 'exit' để thoát.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nBạn: ")
            if user_input.lower() in ["quit", "exit"]:
                print("Tạm biệt!")
                break
            if not user_input.strip():
                continue
                
            result = agent.reply(user_id, thread_id, user_input)
            
            print(f"\nAgent: {result['response']}")
            
            # In ra các thông số theo thời gian thực để bạn dễ thấy cách Memory hoạt động
            prompt_tokens = result["prompt_tokens_processed"]
            total_tokens = result["token_usage"]
            compactions = agent.compaction_count(thread_id)
            user_file = agent.profile_store.read_text(user_id)
            
            print("\n" + "-"*40)
            print("[DEBUG] Trạng thái Memory của hệ thống:")
            print(f"  • Prompt Context Load : {prompt_tokens} tokens")
            print(f"  • Total Tokens Usage  : {total_tokens} tokens")
            print(f"  • Số lần nén (Compact): {compactions} lần")
            print("  • Dữ liệu bền vững (User.md):")
            if user_file.strip():
                for line in user_file.splitlines():
                    print(f"      > {line}")
            else:
                print("      > (chưa có thông tin)")
            print("-"*40)
            
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"\n[Lỗi]: {e}")

if __name__ == "__main__":
    main()
