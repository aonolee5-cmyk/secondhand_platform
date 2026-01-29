class DFAFilter:
    def __init__(self):
        self.keyword_chains = {}  # 关键词链
        self.delimit = '\x00'    # 结束符

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if isinstance(level, dict):
            level[self.delimit] = 0

    def filter(self, message, repl="*"):
        """
        过滤函数：将敏感词替换为 *
        """
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1
        return "".join(ret)

    def contains_any(self, message):
        """
        判断是否包含敏感词
        """
        message = message.lower()
        for i in range(len(message)):
            level = self.keyword_chains
            for char in message[i:]:
                if char in level:
                    if self.delimit in level[char]:
                        return True
                    level = level[char]
                else:
                    break
        return False