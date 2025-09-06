import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
import re

# Load environment variables from .env file
load_dotenv()

class DocumentationChatBot:
    def __init__(self, docs_folder="documentation-generated", api_key=None):
        self.memory = ConversationBufferWindowMemory(k=5, return_messages=True)
        self.docs_folder = docs_folder
        self.documents = self._load_documents()
        
        # Initialize LLM (you can also use other models)
        try:
            # Use provided api_key or get from environment
            openai_key = api_key or os.getenv("OPENAI_API_KEY")
            
            if not openai_key:
                raise ValueError("No OpenAI API key found")
            
            self.llm = OpenAI(
                openai_api_key=openai_key,
                temperature=0.7,
                max_tokens=500
            )
            self.use_llm = True
            print("✅ OpenAI LLM initialized successfully!")
            
        except Exception as e:
            print(f"❌ LLM API not configured or failed: {str(e)}")
            print("Using fallback responses instead.")
            self.use_llm = False
        
        # Create the prompt template with persona
        self.prompt_template = self._create_prompt_template()
        
        if self.use_llm:
            # Initialize LLM chain without memory (we'll handle memory manually)
            self.llm_chain = LLMChain(
                llm=self.llm,
                prompt=self.prompt_template,
                verbose=False
            )
    
    def _create_prompt_template(self):
        """Create a comprehensive prompt template with persona"""
        template = """You are DocBot, an expert technical documentation assistant with a friendly and helpful personality. You have deep knowledge of software development, APIs, databases, and technical systems.

PERSONA TRAITS:
- You are patient, thorough, and always eager to help developers
- You explain complex concepts in simple terms
- You provide practical examples and code snippets when relevant
- You ask clarifying questions if the user's request is unclear
- You admit when you don't know something rather than guessing

CONTEXT INFORMATION:
Here is the relevant documentation that might help answer the user's question:

{relevant_docs}

CONVERSATION HISTORY:
{history}

INSTRUCTIONS:
1. Analyze the user's question carefully
2. Use the provided documentation to give accurate, specific answers
3. If the documentation doesn't contain the answer, say so clearly
4. Provide code examples, step-by-step instructions, or explanations as needed
5. Be conversational and helpful, not robotic
6. If asked about something not in the docs, offer to help find alternative solutions

USER QUESTION: {question}

HELPFUL RESPONSE:"""

        return PromptTemplate(
            input_variables=["relevant_docs", "history", "question"],
            template=template
        )
    
    def _load_documents(self):
        """Load all documentation files with better error handling"""
        docs = {}
        loaded_count = 0
        
        if not os.path.exists(self.docs_folder):
            print(f"Warning: Documentation folder '{self.docs_folder}' not found")
            return docs
            
        for root, dirs, files in os.walk(self.docs_folder):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            docs[file] = {
                                'content': content,
                                'path': file_path,
                                'title': self._extract_title(content)
                            }
                            loaded_count += 1
                    except Exception as e:
                        print(f"Error loading {file}: {str(e)}")
        
        print(f"📚 Loaded {loaded_count} documentation files")
        return docs
    
    def _extract_title(self, content):
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled Document"
    
    def _search_docs(self, query):
        """Enhanced search with scoring and better matching"""
        relevant_docs = []
        query_lower = query.lower()
        query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 2]
        
        for filename, doc_data in self.documents.items():
            content = doc_data['content']
            content_lower = content.lower()
            title = doc_data['title']
            
            # Calculate relevance score
            score = 0
            matches = []
            
            # Score based on title matches (higher weight)
            for word in query_words:
                if word in title.lower():
                    score += 3
                    matches.append(f"title: {word}")
            
            # Score based on content matches
            for word in query_words:
                word_count = content_lower.count(word)
                score += word_count
                if word_count > 0:
                    matches.append(f"content: {word}({word_count})")
            
            # Look for exact phrases
            if query_lower in content_lower:
                score += 5
                matches.append("exact phrase match")
            
            if score > 0:
                # Extract relevant sections
                relevant_sections = self._extract_relevant_sections(content, query_words)
                
                relevant_docs.append({
                    'filename': filename,
                    'title': title,
                    'content': content,
                    'relevant_sections': relevant_sections,
                    'score': score,
                    'matches': matches
                })
        
        # Sort by relevance score
        relevant_docs.sort(key=lambda x: x['score'], reverse=True)
        return relevant_docs[:3]  # Return top 3 matches
    
    def _extract_relevant_sections(self, content, query_words):
        """Extract relevant sections from content based on query"""
        lines = content.split('\n')
        relevant_sections = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains query words
            if any(word in line_lower for word in query_words):
                # Include context around the match
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                
                section = '\n'.join(lines[start:end])
                if section not in relevant_sections:
                    relevant_sections.append(section)
        
        return relevant_sections[:3]  # Limit to top 3 sections
    
    def _format_docs_for_prompt(self, relevant_docs):
        """Format documentation for the LLM prompt"""
        if not relevant_docs:
            return "No relevant documentation found."
        
        formatted = "RELEVANT DOCUMENTATION:\n\n"
        
        for i, doc in enumerate(relevant_docs, 1):
            formatted += f"Document {i}: {doc['title']} ({doc['filename']})\n"
            formatted += "-" * 50 + "\n"
            
            if doc['relevant_sections']:
                formatted += "Relevant sections:\n"
                for section in doc['relevant_sections']:
                    formatted += f"{section}\n\n"
            else:
                # Fallback to first part of content
                content_preview = doc['content'][:600]
                if len(doc['content']) > 600:
                    content_preview += "..."
                formatted += f"{content_preview}\n\n"
        
        return formatted
    
    def _create_fallback_response(self, user_input, relevant_docs):
        """Create a fallback response when LLM is not available"""
        if not relevant_docs:
            return """I couldn't find specific information about that in the documentation. 

Here are some things you can try:
• Be more specific about what you're looking for
• Check if you're using the correct terminology
• Ask about a related topic that might be documented

Type 'help' to see what I can assist you with!"""
        
        response = "Based on the documentation, here's what I found:\n\n"
        
        for doc in relevant_docs:
            response += f"📄 **From {doc['title']}** ({doc['filename']}):\n"
            
            if doc['relevant_sections']:
                for section in doc['relevant_sections'][:2]:
                    response += f"{section}\n\n"
            else:
                content_preview = doc['content'][:400]
                if len(doc['content']) > 400:
                    content_preview += "..."
                response += f"{content_preview}\n\n"
            
            response += "-" * 40 + "\n\n"
        
        response += "💡 **Need more specific information?** Feel free to ask follow-up questions!"
        return response
    
    def get_response(self, user_input):
        """Generate intelligent response using LLM or fallback"""
        try:
            # Handle special commands
            if user_input.lower() in ['help', 'commands']:
                return self._get_help_response()
            
            if user_input.lower() == 'status':
                return self._get_status_response()
            
            # Search for relevant documentation
            relevant_docs = self._search_docs(user_input)
            
            if self.use_llm:
                # Use LLM for intelligent response
                formatted_docs = self._format_docs_for_prompt(relevant_docs)
                
                # Get conversation history
                history = ""
                messages = self.memory.chat_memory.messages
                for msg in messages[-4:]:  # Last 2 exchanges
                    if hasattr(msg, 'content'):
                        role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
                        history += f"{role}: {msg.content}\n"
                
                # Generate response using the new invoke method
                response = self.llm_chain.invoke({
                    "relevant_docs": formatted_docs,
                    "history": history,
                    "question": user_input
                })
                
                # Extract text from response
                if isinstance(response, dict) and 'text' in response:
                    response_text = response['text']
                else:
                    response_text = str(response)
            else:
                # Use fallback response
                response_text = self._create_fallback_response(user_input, relevant_docs)
            
            # Save to memory manually
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(response_text)
            
            return response_text.strip()
            
        except Exception as e:
            print(f"Debug error: {str(e)}")  # For debugging
            error_response = f"🚨 Sorry, I encountered an error: {str(e)}\n\nPlease try rephrasing your question or contact support."
            return error_response
    
    def _get_help_response(self):
        """Provide help information"""
        return """🤖 **DocBot Help**

I'm your technical documentation assistant! Here's how I can help:

**What I can do:**
• Answer questions about your codebase and documentation
• Explain functions, classes, and APIs
• Provide code examples and usage instructions
• Help with setup and configuration
• Explain technical concepts

**Commands:**
• `help` - Show this help message
• `status` - Show system status
• `clear` - Clear conversation memory
• `reload` - Reload documentation files
• `exit` - End the conversation

**Tips for better answers:**
• Be specific about what you're looking for
• Mention relevant file names or function names
• Ask follow-up questions for clarification

Ask me anything about your documentation! 📚"""
    
    def _get_status_response(self):
        """Provide status information"""
        status = f"""📊 **DocBot Status**

**Documentation:**
• Folder: {self.docs_folder}
• Files loaded: {len(self.documents)}
• LLM enabled: {'✅ Yes' if self.use_llm else '❌ No (using fallback)'}

**Memory:**
• Conversation history: {len(self.memory.chat_memory.messages)} messages
• Window size: {self.memory.k} exchanges

**Available documents:**"""
        
        if self.documents:
            for filename, doc_data in list(self.documents.items())[:5]:
                status += f"\n• {doc_data['title']} ({filename})"
            
            if len(self.documents) > 5:
                status += f"\n• ... and {len(self.documents) - 5} more"
        else:
            status += "\n• No documents loaded"
        
        return status
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        return "🧹 Conversation memory cleared! Fresh start!"
    
    def reload_documents(self):
        """Reload documentation files"""
        self.documents = self._load_documents()
        return f"🔄 Reloaded documentation! Found {len(self.documents)} files."

def main():
    """Enhanced chatbot interface"""
    print("🚀 Starting DocBot - Your Technical Documentation Assistant!")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = DocumentationChatBot()
    
    print(f"📁 Documentation folder: {chatbot.docs_folder}")
    print(f"📚 Loaded {len(chatbot.documents)} documentation files")
    print(f"🤖 LLM enabled: {'Yes' if chatbot.use_llm else 'No (fallback mode)'}")
    print("\nType 'help' for commands, or just ask me anything!")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n🧑‍💻 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("🤖 DocBot: Thanks for using DocBot! Happy coding! 👋")
                break
            
            elif user_input.lower() == 'clear':
                result = chatbot.clear_memory()
                print(f"🤖 DocBot: {result}")
                continue
                
            elif user_input.lower() == 'reload':
                result = chatbot.reload_documents()
                print(f"🤖 DocBot: {result}")
                continue
            
            # Get response
            print("🤖 DocBot: ", end="")
            response = chatbot.get_response(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n🤖 DocBot: Goodbye! 👋")
            break
        except Exception as e:
            print(f"🚨 Error: {str(e)}")

if __name__ == "__main__":
    main()