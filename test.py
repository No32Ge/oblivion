
import threading

from main2 import generate_article

if __name__ == '__main__':
    prompts = ["你好", "你是谁？", "我是谁？"]

    threads = []
    for i, p in enumerate(prompts):
        t = threading.Thread(target=generate_article, args=(p,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


