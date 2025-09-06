import unittest
from chatbot import DocumentationChatBot
import os
import tempfile

class TestDocumentationChatBot(unittest.TestCase):
    
    def setUp(self):
        # Create temporary docs folder for testing
        self.test_docs_dir = tempfile.mkdtemp()
        
        # Create sample documentation
        sample_doc = """# Sample API Documentation
        
## User Management
This module handles user authentication and management.

### Functions:
- create_user(): Creates a new user
- delete_user(): Removes a user
- update_user(): Updates user information
"""
        
        with open(os.path.join(self.test_docs_dir, "sample_api.md"), "w") as f:
            f.write(sample_doc)
        
        self.chatbot = DocumentationChatBot(self.test_docs_dir)
    
    def test_chatbot_initialization(self):
        """Test if chatbot initializes correctly"""
        self.assertIsNotNone(self.chatbot.memory)
        self.assertIsNotNone(self.chatbot.documents)
    
    def test_document_loading(self):
        """Test if documents are loaded correctly"""
        self.assertGreater(len(self.chatbot.documents), 0)
        self.assertIn("sample_api.md", self.chatbot.documents)
    
    def test_search_functionality(self):
        """Test document search"""
        results = self.chatbot._search_docs("user management")
        self.assertGreater(len(results), 0)
        self.assertIn("User Management", results[0])
    
    def test_response_generation(self):
        """Test response generation"""
        response = self.chatbot.get_response("How do I create a user?")
        self.assertIsNotNone(response)
        self.assertIn("create_user", response.lower())
    
    def test_memory_functionality(self):
        """Test conversation memory"""
        # First interaction
        self.chatbot.get_response("Tell me about user management")
        
        # Check if memory stores the conversation
        messages = self.chatbot.memory.chat_memory.messages
        self.assertGreater(len(messages), 0)
    
    def test_no_relevant_docs(self):
        """Test response when no relevant docs found"""
        response = self.chatbot.get_response("random unrelated query xyz123")
        self.assertIn("couldn't find", response.lower())

def run_tests():
    """Run all chatbot tests"""
    print("Running ChatBot Tests...")
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()