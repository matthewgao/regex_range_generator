#! /usr/bin/env python3
# 用于生成一个匹配一个数字范围的正则表达式 比如 1 < x < 1001:  ([1-9][0-9][0-9]|[1-9][0-9]|[1-9]|100[0-1])$
# 原理是建立一棵10叉的树，然后深度优先遍历这个数，判断每个节点的子树是否为Full, (子节点0~9都存在为一个Full节点)
# 然后广度优先遍历这个数，把节点中所有full节点直接写成[m-n][0-9]这样， 否则则单独处理
# 最终所有结果|一下就可以了

class NumberNode:
    def __init__(self, num_str, deep):
        self.is_full = False
        self.value = None
        self.node_list = None
        self.deep = deep
        if num_str == "root":
            self.value = "root"
            return
        self.__append(num_str)

    def is_full_node(self):
        if self.node_list is None:
            self.is_full = True
            return self.is_full

        for num in range(0,9+1):
            if str(num) not in self.node_list.keys():
                self.is_full = False
                return self.is_full
            if self.node_list[str(num)] is None:
                self.is_full = False
                return self.is_full
            if not self.node_list[str(num)].is_full:
                self.is_full = False
                return self.is_full

        self.is_full = True
        return self.is_full

    def __append(self, num):
        num_str = self.padding(num)
        rest, value = NumberNode.left_shift_str(num_str)
        self.value = value

        if rest is not None:
            if self.deep - 1 <= 0:
                raise Exception("deep is not enough")
            if self.node_list is None:
                self.node_list = dict()
            _, next_value = NumberNode.left_shift_str(rest)
            if next_value not in self.node_list.keys():
                self.node_list[next_value] = NumberNode(rest, self.deep-1)
            else:
                self.node_list[next_value].__append(rest)

    def add(self, num):
        if num == "0":
            raise Exception("0 is unacceptable, must >0")

        num_str = self.padding(num)
        rest, value = NumberNode.left_shift_str(num_str)

        if rest is None:
            if self.node_list is None:
                self.node_list = dict()
            self.node_list[value] = None
        else:
            if self.deep - 1 <= 0:
                raise Exception("deep is not enough")
            if self.node_list is None:
                self.node_list = dict()

            if value not in self.node_list.keys():
                self.node_list[value] = NumberNode(num_str, self.deep)
            else:
                self.node_list[value].__append(num_str)

    def padding(self, num):
        if len(str(num)) < self.deep:
            return zero_str(self.deep - len(str(num))) + str(num)
        return str(num)

    # 遍历校验所有节点是否为full
    def build(self):
        if self.node_list is None:
            self.is_full_node()
            return 
        for v in self.node_list.values():
            if v is not None:
                v.build()
        self.is_full_node()

    # 生成最终正则表达式
    def get_regex(self):
        l = self.generate()
        output = ""
        first = True
        for elem in l:
            if first:
                output = self.remove_zero_prefix(elem)
                first = False
            else:
                output = output + "|" + self.remove_zero_prefix(elem)
        return "({0})$".format(output)

    def remove_zero_prefix(self, elem):
        rest, num = self.left_shift_str(elem)
        while num == "0" and rest is not None:
            rest, num = self.left_shift_str(rest)
            if num != "0":
                return num+rest
        return num+rest

    def get_all_list(self):
        full_list = list()
        not_full_list = list()
        for k in self.node_list.keys():
            # this "if clause" is only for root case
            if self.node_list[k] is None:
                full_list.append(k)
                continue

            if self.node_list[k].is_full:
                full_list.append(k)
            else:
                not_full_list.append(k)
        return full_list, not_full_list

    def handle_full_node(self, full_list):
        full_output = list()
        if len(full_list) >= 1:
            min_value, max_value = min(full_list), max(full_list)
            full_output.append(self.get_value() + self.regex_range(min_value, max_value) + self.regex_number(self.deep-1))
        return full_output

    def handle_not_full_node(self, not_full_list):
        not_full_output = list()
        for nfle in not_full_list:
            if self.node_list[nfle] is not None:
                vv = self.node_list[nfle].generate()
                print(self.gen_space(), "nest_generate", vv)
                if vv is None:
                    not_full_output.append(self.get_value())
                else:
                    not_full_output = not_full_output + self.cons(self.get_value(), vv)
                    print(self.gen_space(), "nest_generate_output", not_full_output)
            else:
                not_full_output.append(self.get_value() + nfle)
        return not_full_output

    def generate_root(self):
        not_full_output = list()
        # print(self.gen_space(), "root_node_list" ,self.node_list.keys(), self.value)

        full_list, not_full_list = self.get_all_list()

        # print(self.gen_space(), "root_value", self.get_value(), "full_list",full_list)
        # print(self.gen_space(), "root_value", self.get_value(), "not_full_list",not_full_list)

        # root节点有点特殊，他没有value值，只保存子节点，所以这里要单独处理
        full_output = self.handle_full_node(full_list)
        for nfle in not_full_list:
            if self.node_list[nfle] is not None:
                vv = self.node_list[nfle].generate()
                print(self.gen_space(), "nest_generate", vv)
                if vv is None:
                    not_full_output.append(nfle)
                else:
                    not_full_output = not_full_output + vv
                    print(self.gen_space(), "nest_generate_output", not_full_output)
            else:
                not_full_output.append(nfle)

        return full_output + not_full_output

    def generate(self):
        if self.is_full:
            return self.get_value() + self.regex_number(self.deep)

        if self.value == "root":
            return self.generate_root()

        # print(self.gen_space(), "node_list" ,self.node_list.keys(), self.value)
        full_list, not_full_list = self.get_all_list()
        # print(self.gen_space(), "value", self.get_value(), "full_list",full_list)
        # print(self.gen_space(), "value", self.get_value(), "not_full_list",not_full_list)

        full_output = self.handle_full_node(full_list)
        not_full_output = self.handle_not_full_node(not_full_list)
   
        return full_output + not_full_output

    def cons(self, prefix , poss_list):
        output = list()
        for elem in poss_list:
            output.append(prefix+elem)
        return output

    def regex_range(self, start, end):
        if start == end:
            return start
        return "[{0}-{1}]".format(start, end)

    def dump(self):
        print(self.gen_space(), "value", self.value, " IsFull", self.is_full)
        if self.node_list is None:
            return

        for k in self.node_list.keys():
            v = self.node_list[k]
            if v is not None:
                v.dump()

    def regex_number(self, times):
        output = ""
        for _ in range(0, times-1):
            output = output + "[0-9]"
        return output

    def gen_space(self):
        output = ""
        for _ in range(0, self.deep):
            output = output + "   "
        return output

    @staticmethod
    def left_shift(number):
        number_str = str(number)
        if len(number_str) == 1:
            return None, number
        return int(number_str[1:]), int(number_str[0])
        
    @staticmethod
    def left_shift_str(number_str):
        if len(number_str) == 1:
            return None, number_str
        return number_str[1:], number_str[0]

    def get_value(self):
        if self.value == "root" or self.value is None:
            return ""
        return self.value

def zero_str(l) :
    arr = ['0'] * l
    return ''.join(arr)

if __name__ == "__main__":
    nn = NumberNode("root", 4)
    for k in range(1,1001 +1):
        # print(k)
        nn.add(str(k))
    nn.build()
    nn.dump()
    print(nn.get_regex())
