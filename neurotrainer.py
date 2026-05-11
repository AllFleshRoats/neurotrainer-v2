from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
import random
import json
import os

class KnowledgeApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.filename = "knowledge_base.json"
        self.topics = {}
        self.current_topic = None
        self.current_questions = []
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        
        self.load_data()
        self.build_main_ui()
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.topics = json.load(f)
            except:
                self.topics = {}
    
    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.topics, f, ensure_ascii=False, indent=2)
    
    def build_main_ui(self):
        self.clear_widgets()
        
        self.add_widget(Label(text="⚡ Нейро-тренажер", font_size='24sp', size_hint_y=0.1))
        
        buttons_data = [
            ("📝 Добавить тему", self.show_add_topic),
            ("📚 Все темы", self.show_topics),
            ("🤖 Авто-генерация", self.show_ai_generate),
            ("🎲 Начать тест", self.show_test_select),
            ("🗑️ Удалить тему", self.show_delete_topic),
        ]
        
        for text, func in buttons_data:
            btn = Button(text=text, size_hint_y=0.1, background_color=(0.2, 0.4, 0.6, 1))
            btn.bind(on_press=func)
            self.add_widget(btn)
        
        self.output_label = Label(text="Добро пожаловать!", size_hint_y=0.3, 
                                   halign='left', valign='top')
        self.output_label.bind(size=self.output_label.setter('text_size'))
        self.add_widget(self.output_label)
    
    def update_output(self, text):
        self.output_label.text = text
    
    def show_add_topic(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text="Название темы:"))
        topic_input = TextInput(multiline=False)
        content.add_widget(topic_input)
        
        content.add_widget(Label(text="Вопросы (Вопрос|Ответ, по одному на строку):"))
        questions_input = TextInput()
        content.add_widget(questions_input)
        
        def save(instance):
            topic = topic_input.text.strip()
            if not topic:
                return
            
            questions = []
            for line in questions_input.text.strip().split('\n'):
                if '|' in line:
                    q, a = line.split('|', 1)
                    questions.append({"question": q.strip(), "answer": a.strip()})
            
            if questions:
                self.topics[topic] = questions
                self.save_data()
                self.update_output(f"✅ Тема '{topic}' добавлена! ({len(questions)} вопросов)")
                popup.dismiss()
        
        btn_save = Button(text="Сохранить", size_hint_y=0.15)
        btn_save.bind(on_press=save)
        content.add_widget(btn_save)
        
        popup = Popup(title="Добавить тему", content=content, size_hint=(0.9, 0.8))
        popup.open()
    
    def show_topics(self, instance):
        if not self.topics:
            self.update_output("⚠️ Нет добавленных тем!")
            return
        
        text = "📚 Доступные темы:\n\n"
        for topic, cards in self.topics.items():
            text += f"• {topic}: {len(cards)} вопросов\n"
        self.update_output(text)
    
    def show_ai_generate(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text="Введите тему для генерации 10 вопросов:"))
        topic_input = TextInput(multiline=False)
        content.add_widget(topic_input)
        
        def generate(instance):
            topic = topic_input.text.strip()
            if not topic:
                return
            
            questions = []
            for i in range(10):
                questions.append({
                    "question": f"Вопрос {i+1} по теме '{topic}'?",
                    "answer": f"Ответ на вопрос {i+1} по теме '{topic}'"
                })
            
            self.topics[f"AI: {topic}"] = questions
            self.save_data()
            self.update_output(f"✅ Сгенерировано 10 вопросов по теме '{topic}'")
            popup.dismiss()
        
        btn_gen = Button(text="Сгенерировать", size_hint_y=0.15)
        btn_gen.bind(on_press=generate)
        content.add_widget(btn_gen)
        
        popup = Popup(title="Авто-генерация", content=content, size_hint=(0.8, 0.4))
        popup.open()
    
    def show_test_select(self, instance):
        if not self.topics:
            self.update_output("⚠️ Нет тем для теста!")
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Выберите тему:"))
        
        scroll = ScrollView()
        btn_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        btn_layout.bind(minimum_height=btn_layout.setter('height'))
        
        for topic in self.topics.keys():
            btn = Button(text=topic, size_hint_y=None, height=50)
            btn.bind(on_press=lambda x, t=topic: self.start_test(t))
            btn_layout.add_widget(btn)
        
        scroll.add_widget(btn_layout)
        content.add_widget(scroll)
        
        popup = Popup(title="Выбор темы", content=content, size_hint=(0.9, 0.7))
        popup.open()
    
    def start_test(self, topic):
        self.current_topic = topic
        self.current_questions = random.sample(self.topics[topic], len(self.topics[topic]))
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.next_question()
    
    def next_question(self):
        if self.current_index >= len(self.current_questions):
            self.show_results()
            return
        
        q = self.current_questions[self.current_index]
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Вопрос {self.current_index + 1}/{len(self.current_questions)}", font_size='14sp'))
        content.add_widget(Label(text=q['question'], font_size='16sp', size_hint_y=0.4))
        
        answer_input = TextInput(multiline=False, hint_text="Ваш ответ")
        content.add_widget(answer_input)
        
        def submit(instance):
            user_ans = answer_input.text.strip()
            correct = q['answer'].strip()
            is_correct = user_ans.lower() == correct.lower()
            
            self.user_answers.append({
                "question": q['question'],
                "user_answer": user_ans if user_ans else "(нет ответа)",
                "correct_answer": correct,
                "is_correct": is_correct
            })
            
            if is_correct:
                self.score += 1
            
            popup.dismiss()
            self.current_index += 1
            self.next_question()
        
        btn_submit = Button(text="Ответить", size_hint_y=0.15)
        btn_submit.bind(on_press=submit)
        content.add_widget(btn_submit)
        
        popup = Popup(title=f"Тест: {self.current_topic}", content=content, size_hint=(0.9, 0.6))
        popup.open()
    
    def show_results(self):
        percentage = (self.score / len(self.current_questions)) * 100
        
        text = f"🏆 Результаты теста\n\n"
        text += f"Тема: {self.current_topic}\n"
        text += f"Правильных: {self.score}/{len(self.current_questions)}\n"
        text += f"Процент: {percentage:.1f}%\n\n"
        
        if percentage == 100:
            text += "🏆 Идеально!"
        elif percentage >= 70:
            text += "👍 Хорошо!"
        else:
            text += "📖 Попробуйте ещё раз!"
        
        text += "\n\n📝 Разбор:\n"
        for i, ans in enumerate(self.user_answers, 1):
            mark = "✅" if ans['is_correct'] else "❌"
            text += f"\n{mark} {i}. {ans['question']}\n"
            text += f"   Ваш: {ans['user_answer']}\n"
            if not ans['is_correct']:
                text += f"   Правильный: {ans['correct_answer']}\n"
        
        self.update_output(text)
    
    def show_delete_topic(self, instance):
        if not self.topics:
            self.update_output("⚠️ Нет тем для удаления!")
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Выберите тему для удаления:"))
        
        for topic in list(self.topics.keys()):
            btn = Button(text=topic, size_hint_y=0.15, background_color=(0.6, 0.2, 0.2, 1))
            btn.bind(on_press=lambda x, t=topic: self.delete_topic_confirmed(t))
            content.add_widget(btn)
        
        popup = Popup(title="Удалить тему", content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def delete_topic_confirmed(self, topic):
        del self.topics[topic]
        self.save_data()
        self.update_output(f"🗑️ Тема '{topic}' удалена")

class NeuroTrainerApp(App):
    def build(self):
        return KnowledgeApp()

if __name__ == "__main__":
    NeuroTrainerApp().run()