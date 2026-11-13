import json
from app import app
from models import db, Level, Test, Question

def seed_interactive():
    with app.app_context():
        # Check if already seeded
        existing = Test.query.filter_by(title="Đề Thi Trực Tuyến: Từ Vựng Công Nghệ & Giao Tiếp (Interactive)").first()
        if existing:
            print(f"Interactive test already exists with ID: {existing.id}")
            return existing.id

        level = Level.query.filter_by(code='B1').first() or Level.query.first()
        if not level:
            print("No level found!")
            return None

        test = Test(
            level_id=level.id,
            title="Đề Thi Trực Tuyến: Từ Vựng Công Nghệ & Giao Tiếp (Interactive)",
            description="Bài test trực tuyến tương tác theo ảnh mẫu: gồm 15 câu chọn từ điền vào câu dạng menu thả xuống và các câu trắc nghiệm chọn câu trả lời.",
            test_format='interactive',
            ppt_filename=None,
            ppt_filepath=None,
            slides_folder=None,
            audio_filename=None,
            audio_filepath=None,
            total_slides=0,
            time_limit_minutes=15,
            total_questions=17,
            pass_percentage=50,
            is_active=True
        )
        db.session.add(test)
        db.session.commit()

        questions_data = [
            # 1-15: Cloze dropdown questions (from Screenshot 1)
            {
                "num": 1,
                "type": "dropdown_cloze",
                "text": "A power source such as a lithium-ion [battery] can be recharged easily.",
                "correct": "battery",
                "options": ["battery", "network", "voicemail", "apps", "ringtones"]
            },
            {
                "num": 2,
                "type": "dropdown_cloze",
                "text": "With [caller] ID, it is possible to see who is trying to phone you.",
                "correct": "caller",
                "options": ["caller", "waiting", "spam", "text", "data"]
            },
            {
                "num": 3,
                "type": "dropdown_cloze",
                "text": "If you activate the call [waiting] you will hear a beep when someone else tries to call you.",
                "correct": "waiting",
                "options": ["waiting", "voicemail", "ringtones", "instant", "attachment"]
            },
            {
                "num": 4,
                "type": "dropdown_cloze",
                "text": "The phone was set to go to [voicemail] after 3 rings on the telephone.",
                "correct": "voicemail",
                "options": ["voicemail", "battery", "caller", "scanning", "apps"]
            },
            {
                "num": 5,
                "type": "dropdown_cloze",
                "text": "There are so many musical [ringtones] that can be used for a cell phone these days.",
                "correct": "ringtones",
                "options": ["ringtones", "network", "spam", "data", "instant"]
            },
            {
                "num": 6,
                "type": "dropdown_cloze",
                "text": "The device is programmed to access a 3G [network] to upload all schedules.",
                "correct": "network",
                "options": ["network", "battery", "apps", "voicemail", "attachment"]
            },
            {
                "num": 7,
                "type": "dropdown_cloze",
                "text": "Have you tried any of the cell phone [apps] for setting appointments?",
                "correct": "apps",
                "options": ["apps", "ringtones", "caller", "scanning", "UPC"]
            },
            {
                "num": 8,
                "type": "dropdown_cloze",
                "text": "Jim tried to [text] his manager to let her know he would be late.",
                "correct": "text",
                "options": ["text", "call", "instant", "data", "waiting"]
            },
            {
                "num": 9,
                "type": "dropdown_cloze",
                "text": "He can make calls while driving by using [voice activation].",
                "correct": "voice activation",
                "options": ["voice activation", "network", "ringtones", "spam", "battery"]
            },
            {
                "num": 10,
                "type": "dropdown_cloze",
                "text": "The company cell phones do not support this type of [data] plan.",
                "correct": "data",
                "options": ["data", "voicemail", "UPC", "apps", "text"]
            },
            {
                "num": 11,
                "type": "dropdown_cloze",
                "text": "Try to scan the [UPC] if you want to check what is in the shipment.",
                "correct": "UPC",
                "options": ["UPC", "data", "barcode", "package", "label"]
            },
            {
                "num": 12,
                "type": "dropdown_cloze",
                "text": "Due to problems with [scanning] barcodes, the shipping company couldn't dispatch parcels.",
                "correct": "scanning",
                "options": ["scanning", "reading", "printing", "making", "losing"]
            },
            {
                "num": 13,
                "type": "dropdown_cloze",
                "text": "To contact someone quickly try using [instant] messaging.",
                "correct": "instant",
                "options": ["instant", "direct", "phone", "fast", "email"]
            },
            {
                "num": 14,
                "type": "dropdown_cloze",
                "text": "The document was sent as an [attachment] at the bottom of the email.",
                "correct": "attachment",
                "options": ["attachment", "file", "image", "paper", "letter"]
            },
            {
                "num": 15,
                "type": "dropdown_cloze",
                "text": "Any emails which are not recognized will be sent to the [spam] folder.",
                "correct": "spam",
                "options": ["spam", "trash", "junk", "archive", "draft"]
            },
            # 16-17: MCQ with full sentences (from Screenshot 2)
            {
                "num": 16,
                "type": "single_choice",
                "text": "Choose the best reply to each sentence: \"Can you come to my farewell party tonight?\"",
                "correct": "I'm sorry, I can't change my plans.",
                "options": [
                    "I'm sorry, I can't change my plans.",
                    "I didn't invite you.",
                    "I have to leave early."
                ]
            },
            {
                "num": 17,
                "type": "single_choice",
                "text": "Choose the best reply to each sentence: \"Would you like some coffee or tea?\"",
                "correct": "A cup of coffee, please.",
                "options": [
                    "A cup of coffee, please.",
                    "I don't like cup.",
                    "Yes, it is coffee."
                ]
            }
        ]

        for q in questions_data:
            question = Question(
                test_id=test.id,
                question_number=q["num"],
                question_text=q["text"],
                question_type=q["type"],
                options_json=json.dumps(q["options"]),
                correct_answer=q["correct"],
                slide_number=1,
                points=1.0,
                explanation=""
            )
            db.session.add(question)

        db.session.commit()
        print(f"Created sample interactive test successfully! ID: {test.id}, Total questions: {len(questions_data)}")
        
        # Seed missing tests for A2 and B2
        seed_missing_level_tests()
        return test.id

def seed_missing_level_tests():
    with app.app_context():
        # A2
        lvl_a2 = Level.query.filter_by(code='A2').first()
        if lvl_a2 and not any(t.is_active for t in lvl_a2.tests):
            t_a2 = Test(
                level_id=lvl_a2.id,
                title="Đề Thi Trực Tuyến: Giao Tiếp & Từ Vựng Căn Bản A2",
                description="Bài kiểm tra trực tuyến trình độ A2 đánh giá khả năng phản xạ và từ vựng thông dụng.",
                test_format='interactive',
                time_limit_minutes=15,
                total_questions=5,
                pass_percentage=50,
                is_active=True
            )
            db.session.add(t_a2)
            db.session.commit()
            q_list_a2 = [
                {"num": 1, "type": "dropdown_cloze", "text": "She usually travels to school by [bus] every morning.", "correct": "bus", "opts": ["bus", "train", "plane", "boat"]},
                {"num": 2, "type": "dropdown_cloze", "text": "My brother is very keen on [playing] football on weekends.", "correct": "playing", "opts": ["playing", "listening", "reading", "cooking"]},
                {"num": 3, "type": "single_choice", "text": "Where were you born? - \"I was born in Da Nang city.\"", "correct": "I was born in Da Nang city.", "opts": ["I was born in Da Nang city.", "I am born tomorrow.", "I live here.", "I like Da Nang."]},
                {"num": 4, "type": "single_choice", "text": "How often do you go to the cinema? - \"Once a week.\"", "correct": "Once a week.", "opts": ["Once a week.", "One time yesterday.", "I go cinema.", "Yes, I often."]},
                {"num": 5, "type": "single_choice", "text": "Can I help you with your suitcase? - \"Yes, please. That's very kind of you.\"", "correct": "Yes, please. That's very kind of you.", "opts": ["Yes, please. That's very kind of you.", "No, I am suitcase.", "It is a heavy bag.", "You are welcome."]}
            ]
            for q in q_list_a2:
                q_obj = Question(
                    test_id=t_a2.id,
                    question_number=q["num"],
                    question_text=q["text"],
                    question_type=q["type"],
                    options_json=json.dumps(q["opts"]),
                    correct_answer=q["correct"],
                    points=1.0
                )
                db.session.add(q_obj)
            db.session.commit()
            print(f"Created A2 test: ID {t_a2.id}")

        # B2
        lvl_b2 = Level.query.filter_by(code='B2').first()
        if lvl_b2 and not any(t.is_active for t in lvl_b2.tests):
            t_b2 = Test(
                level_id=lvl_b2.id,
                title="Đề Thi Trực Tuyến: Năng Lực Trung Cấp Cao B2",
                description="Bài kiểm tra trực tuyến trình độ B2 đánh giá ngữ pháp nâng cao, mệnh đề và từ vựng học thuật.",
                test_format='interactive',
                time_limit_minutes=20,
                total_questions=5,
                pass_percentage=60,
                is_active=True
            )
            db.session.add(t_b2)
            db.session.commit()
            q_list_b2 = [
                {"num": 1, "type": "dropdown_cloze", "text": "Despite the heavy rain, the flight [departed] strictly on schedule.", "correct": "departed", "opts": ["departed", "arrived", "cancelled", "delayed"]},
                {"num": 2, "type": "dropdown_cloze", "text": "The scientist was praised for making a major [breakthrough] in renewable energy.", "correct": "breakthrough", "opts": ["breakthrough", "failure", "obstacle", "reduction"]},
                {"num": 3, "type": "single_choice", "text": "Hardly had he arrived home ___ the telephone rang.", "correct": "when", "opts": ["when", "than", "then", "after"]},
                {"num": 4, "type": "single_choice", "text": "It is essential that every candidate ___ the safety instructions carefully.", "correct": "follow", "opts": ["follow", "follows", "followed", "following"]},
                {"num": 5, "type": "single_choice", "text": "Had she known about the meeting, she ___ in advance.", "correct": "would have prepared", "opts": ["would have prepared", "will prepare", "prepared", "had prepared"]}
            ]
            for q in q_list_b2:
                q_obj = Question(
                    test_id=t_b2.id,
                    question_number=q["num"],
                    question_text=q["text"],
                    question_type=q["type"],
                    options_json=json.dumps(q["opts"]),
                    correct_answer=q["correct"],
                    points=1.0
                )
                db.session.add(q_obj)
            db.session.commit()
            print(f"Created B2 test: ID {t_b2.id}")

if __name__ == '__main__':
    seed_interactive()
    seed_missing_level_tests()

