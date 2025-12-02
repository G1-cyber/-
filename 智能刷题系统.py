import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
import sys


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能刷题系统")
        self.root.geometry("750x600")  # 稍微增加高度以适应新控件
        self.root.configure(bg='#f5f7fa')

        # 加载题库数据
        self.questions = self.load_question_bank()

        # 用户数据
        self.user_answers = {}
        self.wrong_questions = set()
        self.current_question_index = 0
        self.current_mode = "all"
        self.current_type_filter = "all"  # 新增：题型筛选

        self.setup_ui()
        self.show_question()

    def load_question_bank(self):
        """加载题库数据 - 简化版本"""
        try:
            # 添加桌面路径到系统路径
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if desktop not in sys.path:
                sys.path.append(desktop)

            # 直接导入合并后的题库
            from combined_question_bank import question_bank
            print(f"✅ 成功加载题库，共{len(question_bank)}题")

            # 统计各题型数量
            type_count = {"single": 0, "multiple": 0, "judge": 0}
            for q in question_bank:
                if q['type'] in type_count:
                    type_count[q['type']] += 1
            print(
                f"📊 题型统计 - 单选: {type_count['single']}题, 多选: {type_count['multiple']}题, 判断: {type_count['judge']}题")

            return question_bank

        except ImportError as e:
            print(f"❌ 导入题库失败: {e}")
            print("⚠️ 使用示例题库")

            # 使用示例题库
            return [
                {
                    "id": 1,
                    "stem": "Python中哪个关键字用于定义函数？",
                    "type": "single",
                    "answer": "A",
                    "options": ["def", "function", "define", "func"],
                    "explanation": "在Python中，使用def关键字来定义函数。"
                },
                {
                    "id": 2,
                    "stem": "以下哪些是Python的基本数据类型？",
                    "type": "multiple",
                    "answer": "ABC",
                    "options": ["int", "str", "list", "class"],
                    "explanation": "int、str、list都是Python的基本数据类型，class是关键字。"
                },
                {
                    "id": 3,
                    "stem": "Python是一种编译型语言。",
                    "type": "judge",
                    "answer": "B",
                    "options": ["正确", "错误"],
                    "explanation": "Python是一种解释型语言，不是编译型语言。"
                },
                {
                    "id": 4,
                    "stem": "下列哪个不是Python的数据类型？",
                    "type": "single",
                    "answer": "D",
                    "options": ["list", "tuple", "dict", "array"],
                    "explanation": "array不是Python的基本数据类型，需要从array模块导入。"
                },
                {
                    "id": 5,
                    "stem": "Python支持多重继承。",
                    "type": "judge",
                    "answer": "A",
                    "options": ["正确", "错误"],
                    "explanation": "Python确实支持多重继承，一个类可以继承多个父类。"
                }
            ]

    def setup_ui(self):
        """设置用户界面 - 增加题型筛选功能"""
        # 标题栏
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=f"智能刷题系统 (共{len(self.questions)}题)",
                               font=("Microsoft YaHei", 16, "bold"),
                               fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # 统计信息栏
        stats_frame = tk.Frame(self.root, bg='#ecf0f1')
        stats_frame.pack(fill='x', padx=15, pady=3)

        stats_data = [
            ("总题数", "total_label", "#3498db"),
            ("已答", "answered_label", "#27ae60"),
            ("正确率", "accuracy_label", "#e74c3c"),
            ("当前模式", "mode_label", "#9b59b6")
        ]

        for text, var_name, color in stats_data:
            frame = tk.Frame(stats_frame, bg='#ecf0f1')
            frame.pack(side='left', expand=True, padx=8)

            label = tk.Label(frame, text="0", font=("Microsoft YaHei", 11, "bold"),
                             bg='#ecf0f1', fg=color)
            label.pack(side='left')
            tk.Label(frame, text=text, font=("Microsoft YaHei", 9),
                     bg='#ecf0f1', fg='#7f8c8d').pack(side='left', padx=(2, 0))
            setattr(self, var_name, label)

        # 控制面板 - 分为上下两行
        control_frame = tk.Frame(self.root, bg='#f5f7fa')
        control_frame.pack(fill='x', padx=15, pady=5)

        # 第一行：模式选择
        mode_frame = tk.Frame(control_frame, bg='#f5f7fa')
        mode_frame.pack(fill='x', pady=3)

        # 练习模式选择
        mode_left_frame = tk.Frame(mode_frame, bg='#f5f7fa')
        mode_left_frame.pack(side='left')

        tk.Label(mode_left_frame, text="练习模式:", font=("Microsoft YaHei", 10),
                 bg='#f5f7fa').pack(side='left', padx=(0, 10))

        self.mode_var = tk.StringVar(value="all")
        modes = [("全部题目", "all"), ("错题重练", "wrong")]
        for text, value in modes:
            tk.Radiobutton(mode_left_frame, text=text, variable=self.mode_var,
                           value=value, command=self.on_filter_change,
                           font=("Microsoft YaHei", 9), bg='#f5f7fa').pack(side='left', padx=5)

        # 题型筛选
        type_right_frame = tk.Frame(mode_frame, bg='#f5f7fa')
        type_right_frame.pack(side='right')

        tk.Label(type_right_frame, text="题型筛选:", font=("Microsoft YaHei", 10),
                 bg='#f5f7fa').pack(side='left', padx=(0, 10))

        self.type_var = tk.StringVar(value="all")
        question_types = [("全部", "all"), ("单选题", "single"), ("多选题", "multiple"), ("判断题", "judge")]
        for text, value in question_types:
            tk.Radiobutton(type_right_frame, text=text, variable=self.type_var,
                           value=value, command=self.on_filter_change,
                           font=("Microsoft YaHei", 9), bg='#f5f7fa').pack(side='left', padx=3)

        # 第二行：导航按钮
        nav_frame = tk.Frame(control_frame, bg='#f5f7fa')
        nav_frame.pack(fill='x', pady=3)

        # 左侧：当前筛选信息
        self.filter_info_label = tk.Label(nav_frame, text="", font=("Microsoft YaHei", 10),
                                          bg='#f5f7fa', fg='#e67e22')
        self.filter_info_label.pack(side='left')

        # 右侧：操作按钮
        button_frame = tk.Frame(nav_frame, bg='#f5f7fa')
        button_frame.pack(side='right')

        buttons = [
            ("⬅️ 上一题", self.previous_question, "#3498db"),
            ("➡️ 下一题", self.next_question, "#2ecc71"),
            ("🎲 随机选题", self.random_question, "#9b59b6"),
            ("🔄 重置进度", self.reset_progress, "#e74c3c")
        ]

        for text, command, color in buttons:
            tk.Button(button_frame, text=text, command=command,
                      font=("Microsoft YaHei", 9), bg=color, fg='white',
                      relief='flat', padx=8).pack(side='left', padx=3)

        # 题目显示区域
        self.question_container = tk.Frame(self.root, bg='white', relief='solid', bd=1, height=400)
        self.question_container.pack(fill='both', expand=True, padx=15, pady=5)
        self.question_container.pack_propagate(False)

        self.update_stats()
        self.update_filter_info()

    def get_filtered_questions(self):
        """获取筛选后的题目列表"""
        questions = self.questions.copy()

        # 首先按题型筛选
        if self.type_var.get() != "all":
            questions = [q for q in questions if q['type'] == self.type_var.get()]

        # 然后按模式筛选（错题重练）
        if self.mode_var.get() == "wrong":
            questions = [q for q in questions if str(q['id']) in self.wrong_questions]

        return questions

    def on_filter_change(self):
        """筛选条件改变回调"""
        self.current_question_index = 0
        filtered_questions = self.get_filtered_questions()

        # 如果当前索引超出范围，调整到有效范围
        if self.current_question_index >= len(filtered_questions) and len(filtered_questions) > 0:
            self.current_question_index = len(filtered_questions) - 1
        elif len(filtered_questions) == 0:
            self.current_question_index = 0

        self.update_filter_info()
        self.show_question()

    def update_filter_info(self):
        """更新筛选信息显示"""
        filtered_questions = self.get_filtered_questions()

        mode_text = "全部题目" if self.mode_var.get() == "all" else "错题重练"
        type_text = {
            "all": "全部题型",
            "single": "单选题",
            "multiple": "多选题",
            "judge": "判断题"
        }[self.type_var.get()]

        info_text = f"当前: {mode_text} + {type_text} (共{len(filtered_questions)}题)"
        self.filter_info_label.config(text=info_text)

        # 更新模式标签
        self.mode_label.config(text=f"{mode_text}+{type_text}")

    def show_question(self):
        """显示当前题目"""
        # 清空当前题目区域
        for widget in self.question_container.winfo_children():
            widget.destroy()

        questions = self.get_filtered_questions()

        if not questions:
            no_question_frame = tk.Frame(self.question_container, bg='white')
            no_question_frame.pack(expand=True, fill='both')

            no_question_label = tk.Label(no_question_frame, text="该筛选条件下暂无题目",
                                         font=("Microsoft YaHei", 14), bg='white', fg='#7f8c8d')
            no_question_label.pack(expand=True)

            # 显示提示信息
            hint_text = ""
            if self.mode_var.get() == "wrong" and len(self.wrong_questions) == 0:
                hint_text = "您还没有错题，继续努力！"
            elif self.mode_var.get() == "wrong" and self.type_var.get() != "all":
                hint_text = f"该题型下暂无错题，试试其他题型或全部题型"
            elif self.type_var.get() != "all":
                hint_text = f"该题型下暂无题目，请检查题库"

            if hint_text:
                hint_label = tk.Label(no_question_frame, text=hint_text,
                                      font=("Microsoft YaHei", 11), bg='white', fg='#e67e22')
                hint_label.pack(pady=10)
            return

        question = questions[self.current_question_index]
        question_id = str(question['id'])

        # 错题重练模式下，题目总是未答状态，可以重新作答
        is_wrong_mode = self.mode_var.get() == "wrong"
        has_answered_in_normal_mode = question_id in self.user_answers and not is_wrong_mode

        # 使用网格布局
        main_frame = tk.Frame(self.question_container, bg='white')
        main_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # 题目头部信息
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 10))

        # 进度信息
        progress_text = f"第{self.current_question_index + 1}/{len(questions)}题 (ID: {question['id']})"
        tk.Label(header_frame, text=progress_text, font=("Microsoft YaHei", 11, "bold"),
                 bg='white', fg='#34495e').pack(side='left')

        # 题型标签
        type_colors = {"single": "#3498db", "multiple": "#e74c3c", "judge": "#27ae60"}
        type_names = {"single": "单选题", "multiple": "多选题", "judge": "判断题"}

        type_label = tk.Label(header_frame, text=type_names[question['type']],
                              font=("Microsoft YaHei", 10, "bold"),
                              bg=type_colors[question['type']], fg='white',
                              padx=8, pady=2)
        type_label.pack(side='right')

        # 错题重练模式提示
        if is_wrong_mode:
            wrong_label = tk.Label(header_frame, text="🔁 错题重练中",
                                   font=("Microsoft YaHei", 9, "bold"),
                                   bg='#fff3cd', fg='#856404', padx=5, pady=2)
            wrong_label.pack(side='right', padx=(0, 10))

        # 题目内容
        stem_frame = tk.Frame(main_frame, bg='white')
        stem_frame.pack(fill='x', pady=5)

        # 计算题目文本所需的高度
        stem_text = question['stem']
        text_height = max(3, min(6, len(stem_text) // 40 + 2))  # 动态调整高度

        stem_text_widget = tk.Text(stem_frame, height=text_height, font=("Microsoft YaHei", 12),
                                   wrap='word', bg='#f8f9fa', relief='flat', padx=10, pady=10)
        stem_text_widget.insert('1.0', stem_text)
        stem_text_widget.config(state='disabled')
        stem_text_widget.pack(fill='x', padx=5, pady=5)

        # 选项区域
        options_frame = tk.Frame(main_frame, bg='white')
        options_frame.pack(fill='both', expand=True, pady=10)

        # 根据题型创建选项
        if question['type'] == 'judge':
            self.option_var = tk.StringVar()
            judge_frame = tk.Frame(options_frame, bg='white')
            judge_frame.pack(anchor='center', pady=15)

            for i, option in enumerate(question['options']):
                rb = tk.Radiobutton(judge_frame, text=option, variable=self.option_var,
                                    value='A' if i == 0 else 'B',
                                    font=("Microsoft YaHei", 12), bg='white',
                                    width=8, height=2)
                rb.pack(side='left', padx=30)

                # 错题重练模式下，恢复之前的答案
                if is_wrong_mode and question_id in self.user_answers:
                    user_answer = self.user_answers[question_id]['selected']
                    if user_answer == ('A' if i == 0 else 'B'):
                        self.option_var.set(user_answer)
        else:
            if question['type'] == 'single':
                self.option_var = tk.StringVar()
                for i, option in enumerate(question['options']):
                    option_frame = tk.Frame(options_frame, bg='white')
                    option_frame.pack(fill='x', pady=4)

                    rb = tk.Radiobutton(option_frame, text=f"{chr(65 + i)}. {option}",
                                        variable=self.option_var, value=chr(65 + i),
                                        font=("Microsoft YaHei", 11), bg='white',
                                        justify='left', wraplength=600)
                    rb.pack(anchor='w', padx=15)

                    # 错题重练模式下，恢复之前的答案
                    if is_wrong_mode and question_id in self.user_answers:
                        user_answer = self.user_answers[question_id]['selected']
                        if user_answer == chr(65 + i):
                            self.option_var.set(user_answer)
            else:  # multiple
                self.option_vars = []
                for i, option in enumerate(question['options']):
                    option_frame = tk.Frame(options_frame, bg='white')
                    option_frame.pack(fill='x', pady=4)

                    var = tk.BooleanVar()
                    cb = tk.Checkbutton(option_frame, text=f"{chr(65 + i)}. {option}",
                                        variable=var, font=("Microsoft YaHei", 11), bg='white',
                                        justify='left', wraplength=600)
                    cb.pack(anchor='w', padx=15)
                    self.option_vars.append(var)

                    # 错题重练模式下，恢复之前的答案
                    if is_wrong_mode and question_id in self.user_answers:
                        user_answer = self.user_answers[question_id]['selected']
                        if chr(65 + i) in user_answer:
                            var.set(True)

        # 显示答题结果（仅在普通模式下且已答题时显示）
        if has_answered_in_normal_mode:
            user_answer = self.user_answers[question_id]
            self.show_answer_result(question, user_answer, is_wrong_mode)
        else:
            # 提交按钮区域
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(pady=15)

            submit_text = "提交答案" if not is_wrong_mode else "重新提交"
            submit_btn = tk.Button(button_frame, text=submit_text, command=self.submit_answer,
                                   font=("Microsoft YaHei", 11), bg='#27ae60', fg='white',
                                   padx=25, pady=8)
            submit_btn.pack()

    def show_answer_result(self, question, user_answer, is_wrong_mode=False):
        """显示答题结果"""
        result_frame = tk.Frame(self.question_container, bg='#f8f9fa')
        result_frame.pack(fill='x', padx=15, pady=10)

        is_correct = user_answer['is_correct']
        result_color = '#27ae60' if is_correct else '#e74c3c'
        result_text = "✅ 回答正确！" if is_correct else "❌ 回答错误！"

        # 错题重练模式下显示不同的提示
        if is_wrong_mode:
            result_text = "🔁 错题重练中" + (" - 本次回答正确！" if is_correct else " - 本次仍回答错误")

        tk.Label(result_frame, text=result_text, font=("Microsoft YaHei", 12, "bold"),
                 fg=result_color, bg='#f8f9fa').pack(pady=5)

        # 答案对比
        answer_frame = tk.Frame(result_frame, bg='#f8f9fa')
        answer_frame.pack(pady=5)

        tk.Label(answer_frame, text=f"正确答案: {question['answer']}",
                 font=("Microsoft YaHei", 10), bg='#f8f9fa').pack(side='left', padx=10)
        tk.Label(answer_frame, text=f"您的答案: {user_answer['selected']}",
                 font=("Microsoft YaHei", 10), bg='#f8f9fa').pack(side='left', padx=10)

        # 解析按钮
        tk.Button(result_frame, text="查看解析",
                  command=lambda: self.show_explanation(question),
                  font=("Microsoft YaHei", 10), bg='#f39c12', fg='white').pack(pady=5)

        # 只在普通模式下自动下一题，错题重练模式下不自动跳转
        if not is_wrong_mode:
            # 3秒后自动下一题（比原来多1秒）
            self.root.after(3000, self.auto_next_question)
        else:
            # 错题重练模式下显示手动操作提示
            hint_label = tk.Label(result_frame, text="请手动点击下一题继续练习",
                                  font=("Microsoft YaHei", 9), bg='#f8f9fa', fg='#666')
            hint_label.pack(pady=5)

    def auto_next_question(self):
        """自动下一题（仅在普通模式下使用）"""
        if self.mode_var.get() != "wrong":  # 只在普通模式下自动跳转
            questions = self.get_filtered_questions()
            if self.current_question_index < len(questions) - 1:
                self.current_question_index += 1
                self.show_question()

    def get_user_answer(self):
        """获取用户答案"""
        questions = self.get_filtered_questions()
        question = questions[self.current_question_index]

        if question['type'] == 'multiple':
            selected = []
            for i, var in enumerate(self.option_vars):
                if var.get():
                    selected.append(chr(65 + i))
            return ''.join(sorted(selected))
        else:
            return self.option_var.get()

    def submit_answer(self):
        """提交答案"""
        questions = self.get_filtered_questions()
        if not questions:
            return

        question = questions[self.current_question_index]
        user_answer = self.get_user_answer()

        if not user_answer:
            messagebox.showwarning("提示", "请选择答案！")
            return

        is_correct = (user_answer == question['answer'])
        question_id = str(question['id'])

        # 错题重练模式下的特殊处理
        is_wrong_mode = self.mode_var.get() == "wrong"

        if is_wrong_mode:
            # 错题重练模式下，更新答题记录但不影响错题集合
            # 只有当用户答对时，才从错题集中移除
            if is_correct and question_id in self.wrong_questions:
                self.wrong_questions.remove(question_id)
        else:
            # 普通模式下正常记录
            if not is_correct:
                self.wrong_questions.add(question_id)
            elif question_id in self.wrong_questions:
                self.wrong_questions.remove(question_id)

        # 更新答题记录
        self.user_answers[question_id] = {
            'selected': user_answer,
            'is_correct': is_correct
        }

        self.update_stats()
        self.show_question()

    def show_explanation(self, question):
        """显示题目解析"""
        explanation_window = tk.Toplevel(self.root)
        explanation_window.title("题目解析")
        explanation_window.geometry("500x300")
        explanation_window.configure(bg='white')
        explanation_window.transient(self.root)
        explanation_window.grab_set()

        # 居中显示
        explanation_window.update_idletasks()
        x = (explanation_window.winfo_screenwidth() - 500) // 2
        y = (explanation_window.winfo_screenheight() - 300) // 2
        explanation_window.geometry(f"+{x}+{y}")

        tk.Label(explanation_window, text="题目解析",
                 font=("Microsoft YaHei", 14, "bold"), bg='white').pack(pady=10)

        text_frame = tk.Frame(explanation_window, bg='white')
        text_frame.pack(fill='both', expand=True, padx=15, pady=5)

        explanation_text = tk.Text(text_frame, font=("Microsoft YaHei", 11),
                                   wrap='word', bg='#f8f9fa', height=10)
        explanation_text.pack(fill='both', expand=True)
        explanation_text.insert('1.0', question.get('explanation', '暂无解析'))
        explanation_text.config(state='disabled')

        # 添加滚动条
        scrollbar = tk.Scrollbar(text_frame, command=explanation_text.yview)
        scrollbar.pack(side='right', fill='y')
        explanation_text.config(yscrollcommand=scrollbar.set)

        tk.Button(explanation_window, text="关闭", command=explanation_window.destroy,
                  font=("Microsoft YaHei", 10), bg='#95a5a6', fg='white', width=10).pack(pady=10)

    def previous_question(self):
        """上一题"""
        questions = self.get_filtered_questions()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()

    def next_question(self):
        """下一题"""
        questions = self.get_filtered_questions()
        if self.current_question_index < len(questions) - 1:
            self.current_question_index += 1
            self.show_question()

    def random_question(self):
        """随机选题"""
        questions = self.get_filtered_questions()
        if questions:
            self.current_question_index = random.randint(0, len(questions) - 1)
            self.show_question()

    def reset_progress(self):
        """重置学习进度"""
        if messagebox.askyesno("确认重置", "确定要重置所有学习进度吗？\n这将清除所有答题记录和错题记录。"):
            self.user_answers.clear()
            self.wrong_questions.clear()
            self.current_question_index = 0
            self.update_stats()
            self.show_question()
            messagebox.showinfo("重置成功", "学习进度已重置！")

    def update_stats(self):
        """更新统计信息"""
        total = len(self.questions)
        answered = len(self.user_answers)
        correct = sum(1 for ans in self.user_answers.values() if ans['is_correct'])
        accuracy = (correct / answered * 100) if answered > 0 else 0

        self.total_label.config(text=str(total))
        self.answered_label.config(text=str(answered))
        self.accuracy_label.config(text=f"{accuracy:.1f}%")


def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()