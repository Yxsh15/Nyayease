import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.vector_service import VectorService
import json
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.vector_service = VectorService()
        
    async def answer_legal_query(self, query: str, language: str = "en", document_context: Optional[str] = None) -> Dict[str, Any]:
        """Answer legal queries using RAG approach"""
        try:
            # Get relevant documents from vector database
            search_results = await self.vector_service.similarity_search(query, k=5)
            
            if not search_results:
                return {
                    "response": "I couldn't find relevant legal information for your query. Please try rephrasing your question.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Prepare context from search results
            context = self._prepare_context(search_results)
            
            # Create prompt
            prompt = self._create_legal_prompt(query, context, language, document_context)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse response
            parsed_response = self._parse_ai_response(response.text, search_results)
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error in AI service: {str(e)}")
            return {
                "response": "I'm sorry, I encountered an error while processing your query. Please try again.",
                "sources": [],
                "confidence": 0.0
            }
    
    async def explain_constitution_article(self, article: str, language: str = "en") -> Dict[str, Any]:
        """Explain specific constitutional articles"""
        query = f"Article {article} Indian Constitution meaning explanation"
        return await self.answer_legal_query(query, language)
    
    async def analyze_legal_scenario(self, scenario: str, scenario_type: str, language: str = "en") -> Dict[str, Any]:
        """Analyze real-life legal scenarios"""
        scenario_queries = {
            "landlord_dispute": "tenant rights landlord dispute rental law",
            "police_trouble": "police rights arrest procedure legal rights",
            "money_recovery": "debt recovery civil procedure money lending",
            "harassment": "harassment law women protection legal remedies",
            "property_dispute": "property dispute civil law land rights",
            "employment": "labor law employment rights workplace harassment"
        }
        
        base_query = scenario_queries.get(scenario_type, scenario)
        full_query = f"{base_query} {scenario}"
        
        response = await self.answer_legal_query(full_query, language)
        
        # Add scenario-specific advice
        response["scenario_advice"] = self._get_scenario_advice(scenario_type)
        
        return response
    
    async def analyze_legal_document(self, document_text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze uploaded legal documents"""
        try:
            prompt = f"""
            Analyze this legal document and provide a clear, simple explanation in {language}:
            
            Document: {document_text}
            
            Please provide:
            1. What type of legal document this is
            2. Key points in simple language
            3. What action (if any) is required
            4. Important dates or deadlines
            5. Your legal rights in this situation
            
            Respond in a helpful, non-technical way that a common person can understand.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "analysis": response.text,
                "document_type": self._identify_document_type(document_text),
                "urgency_level": self._assess_urgency(document_text),
                "recommended_action": self._suggest_action(response.text)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {
                "analysis": "Error analyzing document. Please try again.",
                "document_type": "unknown",
                "urgency_level": "medium",
                "recommended_action": "Consult a legal expert"
            }
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Prepare context from search results"""
        context_parts = []
        for result in search_results[:3]:  # Use top 3 results
            source = result["metadata"].get("source", "Unknown")
            content = result["content"][:500]  # Limit content length
            context_parts.append(f"Source: {source}\nContent: {content}")
        
        return "\n\n".join(context_parts)
    
    def _create_legal_prompt(self, query: str, context: str, language: str, document_context: Optional[str] = None) -> str:
        """Create structured prompt for AI"""
        lang_instruction = ""
        if language == "hi":
            lang_instruction = "Please respond in Hindi (हिंदी में जवाब दें)."
        elif language == "mr":
            lang_instruction = "Please respond in Marathi (मराठीत उत्तर द्या)."
        
        document_section = ""
        if document_context:
            document_section = f"""
            The user is asking a question related to the following document:
            ---
            {document_context}
            ---
            Please use this document as primary context for your answer, if relevant.
            """

        return f"""
        You are NyayEase, an AI legal assistant specializing in Indian law. Your role is to help common citizens understand legal concepts in simple, clear language.
        
        Context from Indian legal documents:
        {context}
        
        {document_section}
        
        User Question: {query}
        
        Instructions:
        1. Provide a clear, simple explanation that a non-lawyer can understand
        2. Mention specific laws, articles, or sections that apply
        3. Give practical advice when appropriate
        4. Be empathetic and supportive in your tone
        5. If the query is outside legal domain, politely redirect to legal matters
        {lang_instruction}
        
        Please structure your response with:
        - Direct answer to the question
        - Relevant legal provisions
        - Practical next steps (if applicable)
        - Where to seek further help
        """
    
    def _parse_ai_response(self, response_text: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Parse and structure AI response"""
        sources = list(set([result["metadata"].get("source", "Unknown") for result in search_results]))
        avg_confidence = sum([result["relevance_score"] for result in search_results]) / len(search_results)
        
        return {
            "response": response_text,
            "sources": sources,
            "confidence": avg_confidence,
            "related_sections": self._extract_legal_sections(response_text),
            "formatted_response": response_text  # Assuming the model returns markdown
        }
    
    def _extract_legal_sections(self, response_text: str) -> List[str]:
        """Extract mentioned legal sections from response"""
        import re
        sections = []
        
        # Pattern to find legal references
        patterns = [
            r'Article \d+',
            r'Section \d+[A-Z]*',
            r'IPC \d+[A-Z]*',
            r'CrPC \d+[A-Z]*'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            sections.extend(matches)
        
        return list(set(sections))
    
    def _identify_document_type(self, document_text: str) -> str:
        """Identify type of legal document"""
        text_lower = document_text.lower()
        
        if any(word in text_lower for word in ['notice', 'legal notice']):
            return "Legal Notice"
        elif any(word in text_lower for word in ['summons', 'court', 'civil suit']):
            return "Court Summons"
        elif any(word in text_lower for word in ['fir', 'police', 'complaint']):
            return "Police Complaint/FIR"
        elif any(word in text_lower for word in ['contract', 'agreement']):
            return "Legal Agreement"
        else:
            return "Legal Document"
    
    def _assess_urgency(self, document_text: str) -> str:
        """Assess urgency of legal document"""
        urgent_keywords = ['urgent', 'immediate', 'within', 'days', 'summons', 'notice']
        text_lower = document_text.lower()
        
        if any(word in text_lower for word in urgent_keywords):
            return "high"
        else:
            return "medium"
    
    def _suggest_action(self, analysis: str) -> str:
        """Suggest recommended action"""
        if "summons" in analysis.lower() or "court" in analysis.lower():
            return "Consult a lawyer immediately and prepare for court appearance"
        elif "notice" in analysis.lower():
            return "Review the notice carefully and consider legal consultation"
        else:
            return "Review the document and seek legal advice if needed"
    
    def _get_scenario_advice(self, scenario_type: str) -> str:
        """Get specific advice for different scenarios"""
        advice_map = {
            "landlord_dispute": "Document all communications with landlord. Know your rights under rent control laws.",
            "police_trouble": "Stay calm, know your rights. You have the right to remain silent and contact a lawyer.",
            "money_recovery": "Maintain proper documentation of loans/debts. Consider filing a civil suit if amount is significant.",
            "harassment": "Document incidents, file complaints with appropriate authorities, seek legal protection.",
            "property_dispute": "Gather all property documents, consider mediation before litigation.",
            "employment": "Know your rights under labor laws, document workplace issues, approach labor court if needed."
        }
        
        return advice_map.get(scenario_type, "Seek appropriate legal consultation for your specific situation.")
