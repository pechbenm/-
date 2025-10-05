import unittest
import os
from tinydb import TinyDB
from app import is_valid_date, is_valid_phone, is_valid_email, detect_field_type, parse_args, find_best_match, main

class TestTemplateMatching(unittest.TestCase):

    def setUp(self):
        self.db = TinyDB('test_templates.json')
        self.db.insert_multiple([
            {"name": "Данные пользователя", "login": "email", "tel": "phone"},
            {"name": "Форма заказа", "customer": "text", "order_id": "text", "order_date": "date", "contact": "phone"},
            {"name": "Запрос информации", "customer_name": "text", "customer_email": "email", "feedback_date": "date", "comments": "text"},
            {"name": "Обратная связь", "requester_name": "text", "requester_email": "email", "request_date": "date", "message": "text"}
        ])

    def tearDown(self):

        if hasattr(self, 'db'):
            self.db.close()
        if os.path.exists('test_templates.json'):
            os.remove('test_templates.json')

    def test_is_valid_date(self):
        self.assertTrue(is_valid_date("25.12.2022"))
        self.assertTrue(is_valid_date("2022-12-25"))
        self.assertFalse(is_valid_date("25/12/2022"))
        self.assertFalse(is_valid_date("2022-02-30"))

    def test_is_valid_phone(self):
        self.assertTrue(is_valid_phone("+7 123 456 78 90"))
        self.assertFalse(is_valid_phone("1234567890"))
        self.assertFalse(is_valid_phone("+7 1234 567 89 00"))

    def test_is_valid_email(self):
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertFalse(is_valid_email("test@.com"))
        self.assertFalse(is_valid_email("test@com"))

    def test_detect_field_type(self):
        self.assertEqual(detect_field_type("25.12.2022"), "date")
        self.assertEqual(detect_field_type("+7 123 456 78 90"), "phone")
        self.assertEqual(detect_field_type("test@example.com"), "email")
        self.assertEqual(detect_field_type("Some random text"), "text")

    def test_parse_args(self):
        args = ["--field1=value1", "--field2=value2"]
        expected = {"field1": "value1", "field2": "value2"}
        self.assertEqual(parse_args(args), expected)

    def test_find_best_match(self):
        inputs1 = {"login": "test@example.com", "tel": "+7 123 456 78 90"}
        inputs2 = {"customer": "John Doe", "order_id": "12345", "order_date": "25.12.2022", "contact": "+7 123 456 78 90"}
        
        self.assertEqual(find_best_match(inputs1), "Данные пользователя")
        self.assertEqual(find_best_match(inputs2), "Форма заказа")
        self.assertIsNone(find_best_match({"unknown": "value"}))

    def test_main(self):
        import sys
        from io import StringIO
        
        test_args = ['app.py', 'get_tpl', '--field=text']
        sys.argv = test_args
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        main()
        
        sys.stdout = sys.__stdout__
        
        self.assertIn('"field": "text"', captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()
#python -m unittest test.py