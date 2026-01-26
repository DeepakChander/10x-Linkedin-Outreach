#!/usr/bin/env python3
"""
AI Context Analyzer for 10x-Outreach-Skill
Intelligent email analysis for IT Support

This module provides email analysis capabilities that integrate with Claude Code.
Since this is a Claude Code skill, Claude Code itself handles AI reasoning.
This module provides structured keyword-based analysis that Claude Code can
use as input for more intelligent processing.

Features:
- Email intent classification (incident, request, change, problem)
- Priority assessment (P1-P4) based on content analysis
- Sentiment detection (frustrated, neutral, urgent)
- Entity extraction (systems, error codes, dates)
- Response suggestions based on patterns
- Structured output for Claude Code integration

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[X] Missing dependency: {e}")
    sys.exit(1)

load_dotenv(Path(__file__).parent.parent / '.env')


class EmailIntent(str, Enum):
    """Email intent categories for IT support."""
    INCIDENT = 'incident'        # Something is broken
    REQUEST = 'request'          # Service request
    CHANGE = 'change'            # Change request
    PROBLEM = 'problem'          # Recurring issue
    INQUIRY = 'inquiry'          # Question/info request
    COMPLAINT = 'complaint'      # Dissatisfaction
    FEEDBACK = 'feedback'        # General feedback
    OTHER = 'other'


class EmailPriority(str, Enum):
    """Priority levels with SLA implications."""
    P1 = 'P1'  # Critical - 1hr response, 4hr resolution
    P2 = 'P2'  # High - 4hr response, 8hr resolution
    P3 = 'P3'  # Medium - 8hr response, 2 days resolution
    P4 = 'P4'  # Low - 24hr response, 7 days resolution


class Sentiment(str, Enum):
    """Email sentiment categories."""
    FRUSTRATED = 'frustrated'
    URGENT = 'urgent'
    NEUTRAL = 'neutral'
    POSITIVE = 'positive'


class AIContextAnalyzer:
    """
    Email context analyzer for IT Support.

    This analyzer provides structured email analysis that integrates with Claude Code.
    Since this is a Claude Code skill, Claude Code itself handles advanced AI reasoning.
    This module provides pattern-based analysis as a foundation.

    Provides analysis for:
    - Intent classification (incident, request, change, problem, etc.)
    - Priority assessment (P1-P4)
    - Sentiment detection
    - Entity extraction (systems, error codes, dates)
    - Response template suggestions

    The output can be used by Claude Code for more nuanced decision-making.
    """

    def __init__(self):
        """Initialize analyzer with keyword patterns."""
        self.base_dir = Path(__file__).parent.parent

        # Initialize keyword patterns for analysis
        self._init_keyword_patterns()

    def _init_keyword_patterns(self):
        """Initialize keyword patterns for fallback analysis."""
        self.urgency_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'down', 'broken', 'crashed', 'blocked', 'cannot work',
            'production', 'outage', 'security', 'breach'
        ]

        self.incident_keywords = [
            'not working', 'broken', 'error', 'failed', 'crash',
            'down', 'issue', 'bug', 'problem', 'unable to'
        ]

        self.request_keywords = [
            'need', 'request', 'please provide', 'can you',
            'would like', 'want to', 'access to', 'new'
        ]

        self.frustrated_keywords = [
            'frustrated', 'annoyed', 'disappointed', 'unacceptable',
            'still not', 'again', 'third time', 'keep happening'
        ]

    def analyze_email(
        self,
        body: str,
        subject: str = '',
        from_field: str = '',
        date: str = ''
    ) -> Dict[str, Any]:
        """
        Analyze email content using pattern matching.

        This method provides structured analysis that Claude Code can use
        for intelligent decision-making. Since this is a Claude Code skill,
        Claude Code itself handles advanced AI reasoning on top of this analysis.

        Args:
            body: Email body text
            subject: Email subject
            from_field: Sender information
            date: Email date

        Returns:
            Dict with analysis results including:
            - intent: Classified email intent
            - priority: P1-P4 priority level
            - sentiment: Detected sentiment
            - entities: Extracted entities
            - key_issues: Main issues identified
            - suggested_response: Template response
            - urgency_signals: Words indicating urgency
            - confidence: Analysis confidence score
        """
        return self._analyze_with_patterns(body, subject, from_field, date)

    def _analyze_with_patterns(
        self,
        body: str,
        subject: str,
        from_field: str,
        date: str
    ) -> Dict[str, Any]:
        """Analyze email using keyword matching (fallback)."""
        text = f"{subject} {body}".lower()

        # Detect intent
        intent = EmailIntent.OTHER
        if any(kw in text for kw in self.incident_keywords):
            intent = EmailIntent.INCIDENT
        elif any(kw in text for kw in self.request_keywords):
            intent = EmailIntent.REQUEST
        elif '?' in body:
            intent = EmailIntent.INQUIRY

        # Detect priority
        priority = EmailPriority.P3  # Default medium
        urgency_matches = [kw for kw in self.urgency_keywords if kw in text]
        if len(urgency_matches) >= 2 or 'critical' in text or 'production' in text:
            priority = EmailPriority.P1
        elif urgency_matches:
            priority = EmailPriority.P2
        elif 'when you have time' in text or 'no rush' in text:
            priority = EmailPriority.P4

        # Detect sentiment
        sentiment = Sentiment.NEUTRAL
        if any(kw in text for kw in self.frustrated_keywords):
            sentiment = Sentiment.FRUSTRATED
        elif urgency_matches:
            sentiment = Sentiment.URGENT
        elif any(kw in text for kw in ['thank', 'appreciate', 'great']):
            sentiment = Sentiment.POSITIVE

        # Extract basic entities
        entities = {
            'systems': self._extract_systems(text),
            'error_codes': self._extract_error_codes(text),
            'dates': self._extract_dates(text),
            'people': [],
            'ticket_refs': self._extract_ticket_refs(text)
        }

        # Generate basic response suggestion
        if intent == EmailIntent.INCIDENT and priority in [EmailPriority.P1, EmailPriority.P2]:
            suggested_response = "I acknowledge your urgent issue and am treating this as a high priority. I'm investigating immediately and will provide an update within the hour."
        elif intent == EmailIntent.REQUEST:
            suggested_response = "Thank you for your request. I've logged this and will review the requirements. I'll follow up with next steps shortly."
        else:
            suggested_response = "Thank you for reaching out. I've received your message and will review it promptly. Please let me know if you have any additional information to share."

        return self._normalize_analysis({
            'intent': intent.value,
            'priority': priority.value,
            'sentiment': sentiment.value,
            'entities': entities,
            'key_issues': [subject] if subject else ['See email body'],
            'suggested_response': suggested_response,
            'urgency_signals': urgency_matches,
            'confidence': 0.75  # Pattern-based analysis confidence
        }, 'pattern')

    def _normalize_analysis(self, analysis: Dict, method: str) -> Dict[str, Any]:
        """Normalize and validate analysis results."""
        # Ensure all required fields exist
        normalized = {
            'intent': analysis.get('intent', 'other'),
            'priority': analysis.get('priority', 'P3'),
            'sentiment': analysis.get('sentiment', 'neutral'),
            'entities': analysis.get('entities', {}),
            'key_issues': analysis.get('key_issues', []),
            'suggested_response': analysis.get('suggested_response', ''),
            'urgency_signals': analysis.get('urgency_signals', []),
            'confidence': analysis.get('confidence', 0.5),
            'analysis_method': method,
            'analyzed_at': datetime.utcnow().isoformat() + 'Z'
        }

        # Validate enum values
        try:
            normalized['intent'] = EmailIntent(normalized['intent']).value
        except ValueError:
            normalized['intent'] = 'other'

        try:
            normalized['priority'] = EmailPriority(normalized['priority']).value
        except ValueError:
            normalized['priority'] = 'P3'

        try:
            normalized['sentiment'] = Sentiment(normalized['sentiment']).value
        except ValueError:
            normalized['sentiment'] = 'neutral'

        return normalized

    def _extract_systems(self, text: str) -> List[str]:
        """Extract system/application names from text."""
        common_systems = [
            'outlook', 'teams', 'sharepoint', 'onedrive', 'excel', 'word',
            'salesforce', 'jira', 'confluence', 'slack', 'zoom', 'vpn',
            'active directory', 'ad', 'email', 'printer', 'network', 'wifi',
            'laptop', 'desktop', 'phone', 'server', 'database', 'website',
            'portal', 'crm', 'erp', 'sap', 'oracle', 'aws', 'azure'
        ]
        found = []
        for system in common_systems:
            if system in text:
                found.append(system)
        return found

    def _extract_error_codes(self, text: str) -> List[str]:
        """Extract error codes from text."""
        patterns = [
            r'error[:\s]+(\d+)',
            r'code[:\s]+([A-Z0-9]+)',
            r'0x[0-9A-Fa-f]+',
            r'ERROR_[A-Z_]+',
            r'\b[A-Z]{2,4}[-_]?\d{3,6}\b'
        ]
        codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            codes.extend(matches)
        return list(set(codes))[:5]  # Limit to 5

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}'
        ]
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches if isinstance(matches[0], str) else [] if not matches else matches)
        return list(set(dates))[:5]

    def _extract_ticket_refs(self, text: str) -> List[str]:
        """Extract ticket/case references from text."""
        patterns = [
            r'ticket[:#\s]+(\d+)',
            r'case[:#\s]+(\d+)',
            r'INC\d+',
            r'REQ\d+',
            r'CHG\d+',
            r'#(\d{4,})'
        ]
        refs = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            refs.extend(matches)
        return list(set(refs))[:5]

    def generate_response(
        self,
        email_body: str,
        analysis: Dict[str, Any],
        tone: str = 'professional'
    ) -> str:
        """
        Generate a response template based on email analysis.

        This provides template-based responses that Claude Code can customize
        for more personalized communication.

        Args:
            email_body: Original email body
            analysis: Analysis results from analyze_email()
            tone: Response tone (professional, friendly, formal)

        Returns:
            Response template text
        """
        return self._generate_response_template(analysis, tone)

    def _generate_response_template(
        self,
        analysis: Dict[str, Any],
        tone: str
    ) -> str:
        """Generate response template based on analysis."""
        intent = analysis.get('intent', 'other')
        priority = analysis.get('priority', 'P3')
        sentiment = analysis.get('sentiment', 'neutral')

        # Priority-based timeframes
        timeframes = {
            'P1': 'within the hour',
            'P2': 'within 4 hours',
            'P3': 'within 1 business day',
            'P4': 'within 2-3 business days'
        }
        timeframe = timeframes.get(priority, 'shortly')

        # Tone adjustments
        greeting = {
            'professional': 'Thank you for contacting us.',
            'friendly': 'Thanks for reaching out!',
            'formal': 'We acknowledge receipt of your correspondence.'
        }.get(tone, 'Thank you for contacting us.')

        # Intent-based templates
        if intent == 'incident':
            if priority in ['P1', 'P2']:
                return f"{greeting} I understand this is an urgent issue affecting your work. I'm treating this as a high priority and will investigate immediately. You can expect an update {timeframe}."
            else:
                return f"{greeting} I've logged your reported issue and will investigate. I'll follow up with findings and next steps {timeframe}."
        elif intent == 'request':
            return f"{greeting} I've received your service request and will review the requirements. I'll provide an update on feasibility and timeline {timeframe}."
        elif intent == 'change':
            return f"{greeting} I've received your change request. I'll assess the impact and requirements, and follow up with a plan {timeframe}."
        elif intent == 'inquiry':
            return f"{greeting} I've received your question and will research the answer. I'll get back to you {timeframe} with the information you need."
        elif intent == 'complaint':
            if sentiment == 'frustrated':
                return f"{greeting} I sincerely apologize for the inconvenience you've experienced. I understand your frustration and am prioritizing this matter. I'll personally follow up {timeframe}."
            else:
                return f"{greeting} I appreciate you bringing this to our attention. I'll review the situation and follow up {timeframe} with how we plan to address your concerns."
        else:
            return f"{greeting} I've received your message and will review it promptly. I'll follow up {timeframe} with a response."


# Factory function
def get_analyzer() -> AIContextAnalyzer:
    """Get AI context analyzer instance."""
    return AIContextAnalyzer()


# CLI for testing
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='AI Context Analyzer')
    parser.add_argument('--test', action='store_true', help='Run test analysis')
    parser.add_argument('--analyze', metavar='TEXT', help='Analyze provided text')

    args = parser.parse_args()

    analyzer = AIContextAnalyzer()

    if args.test:
        test_email = """
        Subject: URGENT - Production server down!

        Hi IT Team,

        The main production server has been down since 10 AM this morning.
        We're getting error 503 when trying to access the website.
        This is affecting all our customers and we're losing sales!

        I've already tried restarting but it comes back with the same error.
        This happened last week too - ticket #12345.

        Please help ASAP - this is critical!

        Thanks,
        John
        """

        print("Analyzing test email...")
        result = analyzer.analyze_email(
            body=test_email,
            subject="URGENT - Production server down!",
            from_field="john@example.com",
            date="2024-01-15"
        )

        print(f"\nAnalysis Result:")
        print(json.dumps(result, indent=2))

    elif args.analyze:
        result = analyzer.analyze_email(body=args.analyze)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
