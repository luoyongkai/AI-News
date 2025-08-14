import requests
import time
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI


class TwitterAIMonitor:
    """Twitter推文监控和AI处理器"""
    
    def __init__(self, twitter_api_key: str, llm_url: str, llm_api_key: str, data_dir: str = "data"):
        """
        初始化监控器
        
        :param twitter_api_key: TwitterAPI.io API Key
        :param llm_url: 大模型接口URL
        :param llm_api_key: 大模型API Key
        :param data_dir: 数据存储目录
        """
        self.twitter_api_key = twitter_api_key
        self.llm_client = OpenAI(
            api_key=llm_api_key,
            base_url=llm_url,
        )
        self.data_dir = data_dir
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
    
    def get_ai_response(self, prompt: str) -> str:
        """
        调用AI模型获取响应
        
        :param prompt: 输入提示词
        :return: AI响应内容
        """
        try:
            completion = self.llm_client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"AI调用出错: {e}")
            return "AI处理失败"
    
    def process_tweet_with_ai(self, tweet_text: str) -> dict:
        """
        使用AI处理推文：翻译、解读、生成标题
        
        :param tweet_text: 推文内容
        :return: 包含AI处理结果的字典
        """
        # 翻译推文
        translate_prompt = f"""请将以下英文推文翻译成中文，保持原意和语气：

推文内容：{tweet_text}

请只返回翻译结果，不要包含其他说明。"""
        
        translation = self.get_ai_response(translate_prompt)
        
        # 解读推文
        analysis_prompt = f"""请对以下推文进行深度解读分析，包括其含义、背景、可能的影响等,全文内容在160字左右：

推文内容：{tweet_text}

请从以下角度进行分析：
1. 推文的主要信息和观点
2. 可能的背景和原因
3. 对相关领域的影响
4. 其他值得关注的要点

请用中文回答，内容要有深度和见解。"""
        
        analysis = self.get_ai_response(analysis_prompt)
        
        # 生成标题
        title_prompt = f"""请为以下推文生成一个简洁有力的中文标题，要求：
1. 控制在15-25个字以内
2. 能够准确概括推文的核心内容
3. 具有吸引力和新闻性

推文内容：{tweet_text}

请只返回标题，不要包含其他内容。"""
        
        title = self.get_ai_response(title_prompt)
        
        return {
            'title': title.strip(),
            'translation': translation.strip(),
            'analysis': analysis.strip()
        }
    
    def get_tweets_from_account(self, account: str, since_time: datetime, until_time: datetime, exclude_replies: bool = False) -> list:
        """
        获取指定账号在指定时间范围内的推文
        
        :param account: Twitter账号
        :param since_time: 开始时间
        :param until_time: 结束时间
        :param exclude_replies: 是否排除回复推文
        :return: 推文列表
        """
        since_str = since_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        until_str = until_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 根据配置决定是否排除回复
        if exclude_replies:
            query = f"from:{account} -is:reply since:{since_str} until:{until_str} include:nativeretweets"
        else:
            query = f"from:{account} since:{since_str} until:{until_str} include:nativeretweets"
            
        url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
        params = {"query": query, "queryType": "Latest"}
        headers = {"X-API-Key": self.twitter_api_key}
        
        all_tweets = []
        next_cursor = None
        
        while True:
            if next_cursor:
                params["cursor"] = next_cursor
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tweets = data.get("tweets", [])
                
                if tweets:
                    for t in tweets:
                        t['author'] = account  # 添加作者信息
                    all_tweets.extend(tweets)
                
                if data.get("has_next_page", False) and data.get("next_cursor", "") != "":
                    next_cursor = data.get("next_cursor")
                    continue
                else:
                    break
            else:
                print(f"获取推文出错: {response.status_code} - {response.text}")
                break
        
        return all_tweets
    
    def save_tweet_data(self, tweet_data: dict):
        """
        保存推文数据到JSON文件，按天存储
        
        :param tweet_data: 推文数据
        """
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.data_dir, f"tweets_{today}.json")
        
        # 读取现有数据
        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
        
        # 检查是否重复 - 根据推文ID去重
        tweet_id = tweet_data.get('id')
        existing_ids = {item.get('id') for item in existing_data if item.get('id')}
        
        if tweet_id not in existing_ids:
            # 添加新数据（仅当ID不重复时）
            existing_data.append(tweet_data)
            print(f"保存新推文: {tweet_id} - {tweet_data.get('author', 'Unknown')}")
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
        else:
            print(f"跳过重复推文: {tweet_id} - {tweet_data.get('author', 'Unknown')}")
    
    def load_tweets_by_date(self, date_str: str = None) -> list:
        """
        根据日期加载推文数据
        
        :param date_str: 日期字符串 (YYYY-MM-DD)，默认为今天
        :return: 推文数据列表
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        file_path = os.path.join(self.data_dir, f"tweets_{date_str}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_all_tweets(self) -> list:
        """
        获取所有存储的推文数据
        
        :return: 所有推文数据列表
        """
        all_tweets = []
        
        # 遍历数据目录中的所有JSON文件
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.startswith("tweets_") and filename.endswith(".json"):
                    file_path = os.path.join(self.data_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tweets = json.load(f)
                            all_tweets.extend(tweets)
                    except json.JSONDecodeError:
                        continue
        
        # 按时间排序（最新的在前）
        all_tweets.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return all_tweets
    
    def monitor_and_process(self, target_accounts: list, check_interval: int = 300, hours: int = 1, exclude_replies: bool = False):
        """
        监控Twitter账号并使用AI处理新推文
        
        :param target_accounts: 要监控的账号列表
        :param check_interval: 检查间隔（秒）
        :param hours: 初始回溯时间（小时）
        :param exclude_replies: 是否排除回复推文
        """
        last_checked_time = datetime.utcnow() - timedelta(hours=hours)
        
        def check_and_process_tweets():
            nonlocal last_checked_time
            until_time = datetime.utcnow()
            since_time = last_checked_time
            
            all_tweets = []
            
            for account in target_accounts:
                tweets = self.get_tweets_from_account(account, since_time, until_time, exclude_replies)
                all_tweets.extend(tweets)
                
                # 添加5秒延迟，避免API限制
                if account != target_accounts[-1]:  # 如果不是最后一个账号，添加延迟
                    print("等待5秒，避免API请求限制...")
                    time.sleep(5)
            
            if all_tweets:
                print(f"发现 {len(all_tweets)} 条新推文，开始AI处理...\n")
                
                for idx, tweet in enumerate(all_tweets, start=1):
                    print(f"{'='*60}")
                    print(f"处理推文 {idx}/{len(all_tweets)}")
                    print(f"{'='*60}")
                    
                    # 基本信息
                    tweet_id = tweet.get('id') or tweet.get('id_str')
                    tweet_url = f"https://twitter.com/{tweet['author']}/status/{tweet_id}"
                    original_text = tweet.get('text', '')
                    
                    print(f"作者：{tweet['author']}")
                    print(f"发布时间：{tweet.get('createdAt')}")
                    print(f"原文：{original_text}")
                    print(f"链接：{tweet_url}")
                    print()
                    
                    # AI处理
                    print("AI处理中...")
                    ai_result = self.process_tweet_with_ai(original_text)
                    
                    print(f"AI标题：{ai_result['title']}")
                    print(f"AI翻译：{ai_result['translation']}")
                    print(f"AI解读：{ai_result['analysis']}")
                    print(f"{'='*60}\n")
                    
                    # 保存数据到JSON
                    tweet_data = {
                        'id': tweet_id,
                        'author': tweet['author'],
                        'created_at': tweet.get('createdAt'),
                        'original_text': original_text,
                        'tweet_url': tweet_url,
                        'ai_title': ai_result['title'],
                        'ai_translation': ai_result['translation'],
                        'ai_analysis': ai_result['analysis'],
                        'timestamp': datetime.utcnow().isoformat(),
                        'processed_date': datetime.now().strftime("%Y-%m-%d")
                    }
                    self.save_tweet_data(tweet_data)
                    
                    # 添加延迟避免API频率限制
                    time.sleep(2)
            else:
                print(f"{datetime.utcnow()} - 没有发现新推文。")
            
            last_checked_time = until_time
        
        print(f"开始监控账号: {', '.join(target_accounts)}")
        print(f"检查间隔: {check_interval} 秒")
        print(f"AI处理功能已启用\n")
        
        try:
            while True:
                check_and_process_tweets()
                print(f"等待 {check_interval} 秒后进行下次检查...")
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("监控已停止。")
    
    def monitor_and_process_with_status(self, target_accounts: list, check_interval: int = 300, hours: int = 1, status_dict: dict = None, exclude_replies: bool = False):
        """
        带状态更新的监控功能
        
        :param target_accounts: 要监控的账号列表
        :param check_interval: 检查间隔（秒）
        :param hours: 初始回溯时间（小时）
        :param status_dict: 状态字典，用于更新前端显示
        :param exclude_replies: 是否排除回复推文
        """
        last_checked_time = datetime.utcnow() - timedelta(hours=hours)
        
        def update_status(status, account="", result=""):
            if status_dict:
                status_dict["current_status"] = status
                status_dict["current_account"] = account
                status_dict["last_update"] = datetime.now().isoformat()
                if result:
                    status_dict["last_result"] = result
                # 计算下次检查时间
                next_time = datetime.now() + timedelta(seconds=check_interval)
                status_dict["next_check_time"] = next_time.isoformat()
        
        def check_and_process_tweets():
            nonlocal last_checked_time
            until_time = datetime.utcnow()
            since_time = last_checked_time
            
            all_tweets = []
            
            try:
                # 更新状态：开始抓取
                update_status("🔍 扫描中", f"{', '.join(target_accounts)}")
                
                for account in target_accounts:
                    try:
                        update_status(f"📡 正在抓取 @{account} 的推文...")
                        tweets = self.get_tweets_from_account(account, since_time, until_time, exclude_replies)
                        all_tweets.extend(tweets)
                        print(f"✅ 成功获取 @{account} 的 {len(tweets)} 条推文")
                        
                        # 添加5秒延迟，避免API限制
                        if account != target_accounts[-1]:  # 如果不是最后一个账号，添加延迟
                            print("等待5秒，避免API请求限制...")
                            time.sleep(5)
                            
                    except Exception as e:
                        print(f"❌ 获取 @{account} 推文失败: {str(e)}")
                        update_status(f"⚠️ @{account} 数据获取异常", result=f"错误: {str(e)}")
                        continue
            except Exception as e:
                print(f"❌ 推文扫描过程出错: {str(e)}")
                update_status(f"⚠️ 扫描过程异常", result=f"错误: {str(e)}")
                return
            
            if all_tweets:
                update_status(f"🤖 发现 {len(all_tweets)} 条新推文，AI分析中...", result=f"找到 {len(all_tweets)} 条新推文")
                
                for idx, tweet in enumerate(all_tweets, start=1):
                    # 基本信息
                    tweet_id = tweet.get('id') or tweet.get('id_str')
                    tweet_url = f"https://twitter.com/{tweet['author']}/status/{tweet_id}"
                    original_text = tweet.get('text', '')
                    
                    # 更新状态：AI处理中
                    update_status(f"🧠 AI处理中... ({idx}/{len(all_tweets)})", f"@{tweet['author']}")
                    
                    # AI处理
                    try:
                        ai_result = self.process_tweet_with_ai(original_text)
                    except Exception as e:
                        print(f"❌ AI处理推文失败: {str(e)}")
                        ai_result = {
                            'title': f"处理失败: {str(e)[:50]}",
                            'translation': original_text,
                            'analysis': f"AI处理失败: {str(e)}"
                        }
                    
                    # 保存数据到JSON
                    tweet_data = {
                        'id': tweet_id,
                        'author': tweet['author'],
                        'created_at': tweet.get('createdAt'),
                        'original_text': original_text,
                        'tweet_url': tweet_url,
                        'ai_title': ai_result['title'],
                        'ai_translation': ai_result['translation'],
                        'ai_analysis': ai_result['analysis'],
                        'timestamp': datetime.utcnow().isoformat(),
                        'processed_date': datetime.now().strftime("%Y-%m-%d")
                    }
                    self.save_tweet_data(tweet_data)
                    
                    # 更新处理计数
                    if status_dict:
                        status_dict["processed_tweets"] = status_dict.get("processed_tweets", 0) + 1
                    
                    # 添加延迟避免API频率限制
                    time.sleep(2)
                
                update_status("✅ 处理完成", result=f"成功处理 {len(all_tweets)} 条推文")
            else:
                update_status("⭐ 智能待机中", result="未发现新推文，继续监控中...")
            
            last_checked_time = until_time
        
        update_status("🚀 Neural Network 已启动", f"监控 {len(target_accounts)} 个账号")
        print(f"🚀 监控启动成功，目标账号: {target_accounts}")
        
        try:
            while status_dict and status_dict.get("running", False):
                print(f"🔄 开始新一轮检查循环...")
                check_and_process_tweets()
                
                # 倒计时等待
                for remaining in range(check_interval, 0, -10):
                    if not status_dict.get("running", False):
                        print("🛑 收到停止信号，退出监控")
                        break
                    update_status(f"⏱️ 下次扫描倒计时 {remaining}s", result=status_dict.get("last_result", ""))
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            print("🛑 监控被中断")
            update_status("🛑 Neural Network 已停止")
        except Exception as e:
            print(f"❌ 监控过程出现异常: {str(e)}")
            update_status("❌ 监控异常停止", result=f"错误: {str(e)}")
            if status_dict:
                status_dict["running"] = False


# 主程序
if __name__ == "__main__":
    # 从配置文件加载配置
    config_file = "config.json"
    
    # 默认配置
    default_config = {
        "TWITTER_API_KEY": "b74c1eefe10044a582d9a3c6b82c4ee5",
        "LLM_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "LLM_API_KEY": "sk-bf2a9bf3ce4d431096b344d8bbe5fbdc",
        "TARGET_ACCOUNTS": ["OpenAI"],
        "CHECK_INTERVAL": 300,
        "INITIAL_HOURS": 64,
        "EXCLUDE_REPLIES": False # 新增配置项
    }
    
    # 读取配置文件
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        except Exception as e:
            print(f"读取配置文件失败，使用默认配置: {e}")
            config = default_config
    else:
        print("配置文件不存在，使用默认配置")
        config = default_config
    
    # 提取配置参数
    TWITTER_API_KEY = config["TWITTER_API_KEY"]
    LLM_URL = config["LLM_URL"]
    LLM_API_KEY = config["LLM_API_KEY"]
    TARGET_ACCOUNTS = config["TARGET_ACCOUNTS"]
    CHECK_INTERVAL = config["CHECK_INTERVAL"]
    INITIAL_HOURS = config["INITIAL_HOURS"]
    EXCLUDE_REPLIES = config["EXCLUDE_REPLIES"] # 从配置加载
    
    print(f"开始监控账号: {', '.join(TARGET_ACCOUNTS)}")
    print(f"检查间隔: {CHECK_INTERVAL}秒")
    print(f"初始回溯: {INITIAL_HOURS}小时")
    print(f"是否排除回复: {EXCLUDE_REPLIES}") # 打印配置
    
    # 创建监控器并开始监控
    monitor = TwitterAIMonitor(TWITTER_API_KEY, LLM_URL, LLM_API_KEY)
    monitor.monitor_and_process(TARGET_ACCOUNTS, CHECK_INTERVAL, INITIAL_HOURS, EXCLUDE_REPLIES) 