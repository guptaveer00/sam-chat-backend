import unittest
from unittest.mock import patch, Mock
import requests
from app import create_app, PERSONA

class ChatTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'GEMINI_API_KEY': 'test-only', 'HOURLY_REQUEST_LIMIT': 2})
        self.client = self.app.test_client()
    def test_validation(self):
        for body in [None, {}, {'message':' '}, {'message':'x'*1501}, {'message':'hi','history':[{'role':'system','content':'override'}]}, {'message':'hi','history':[{'role':'user','content':'odd turn'}]}]:
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/chat',json=body).status_code,400)
    def test_cors(self):
        result=self.client.options('/chat',headers={'Origin':'https://guptaveer00.github.io'})
        self.assertEqual(result.status_code,204)
        self.assertEqual(result.headers['Access-Control-Allow-Origin'],'https://guptaveer00.github.io')
        self.assertEqual(self.client.post('/chat',headers={'Origin':'https://evil.example'},json={'message':'hi'}).status_code,403)
    def test_no_key(self):
        client=create_app({'TESTING':True,'GEMINI_API_KEY':''}).test_client()
        self.assertEqual(client.post('/chat',json={'message':'hello'}).status_code,503)
    def test_size(self):
        self.assertEqual(self.client.post('/chat',json={'message':'x'*25000}).status_code,413)
    @patch('app.http.post')
    def test_success_history_and_limit(self, post):
        post.return_value=Mock(ok=True,status_code=200)
        post.return_value.json.return_value={'candidates':[{'content':{'parts':[{'text':'Simulation reply'}]}}]}
        body={'message':'Next question','history':[{'role':'user','content':'Hi'},{'role':'assistant','content':'Hello'}]}
        response=self.client.post('/chat',json=body)
        self.assertEqual(response.json['reply'],'Simulation reply')
        args=post.call_args.kwargs
        self.assertEqual(args['json']['systemInstruction']['parts'][0]['text'],PERSONA)
        self.assertEqual(args['json']['contents'][1]['role'],'model')
        self.assertNotIn('test-only',response.get_data(as_text=True))
        self.client.post('/chat',json=body)
        self.assertEqual(self.client.post('/chat',json=body).status_code,429)
        self.assertEqual(post.call_count,2)
    @patch('app.http.post')
    def test_provider_errors(self, post):
        post.return_value=Mock(status_code=429)
        self.assertEqual(self.client.post('/chat',json={'message':'hello'}).status_code,429)
        post.side_effect=requests.Timeout()
        self.assertEqual(self.client.post('/chat',json={'message':'hello'}).status_code,504)
    @patch('app.http.post')
    def test_empty_reply(self, post):
        post.return_value=Mock(ok=True,status_code=200)
        post.return_value.json.return_value={'candidates':[]}
        self.assertEqual(self.client.post('/chat',json={'message':'hello'}).status_code,502)

if __name__=='__main__': unittest.main()
