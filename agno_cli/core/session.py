"""
Session management for Agno CLI SDK
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class SessionInfo:
    """Session information"""
    session_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': self.message_count,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """Create from dictionary"""
        return cls(
            session_id=data['session_id'],
            name=data['name'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            message_count=data.get('message_count', 0),
            description=data.get('description', '')
        )


class SessionManager:
    """Manages chat sessions for Agno CLI SDK"""
    
    def __init__(self, sessions_dir: str = "~/.agno_cli/sessions"):
        self.sessions_dir = Path(sessions_dir).expanduser()
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.sessions_file = self.sessions_dir / "sessions.json"
        self.current_session_id: Optional[str] = None
        
        # Load existing sessions
        self._sessions: Dict[str, SessionInfo] = {}
        self.load_sessions()
    
    def load_sessions(self) -> None:
        """Load sessions from file"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)
                
                for session_data in data.get('sessions', []):
                    session_info = SessionInfo.from_dict(session_data)
                    self._sessions[session_info.session_id] = session_info
                    
                self.current_session_id = data.get('current_session_id')
                
            except Exception as e:
                print(f"Warning: Failed to load sessions: {e}")
    
    def save_sessions(self) -> None:
        """Save sessions to file"""
        try:
            data = {
                'current_session_id': self.current_session_id,
                'sessions': [session.to_dict() for session in self._sessions.values()]
            }
            
            with open(self.sessions_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error: Failed to save sessions: {e}")
    
    def create_session(self, name: Optional[str] = None, description: str = "") -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        if name is None:
            name = f"Session {now.strftime('%Y-%m-%d %H:%M')}"
        
        session_info = SessionInfo(
            session_id=session_id,
            name=name,
            created_at=now,
            updated_at=now,
            description=description
        )
        
        self._sessions[session_id] = session_info
        self.current_session_id = session_id
        self.save_sessions()
        
        # Create session directory
        session_dir = self.get_session_dir(session_id)
        session_dir.mkdir(exist_ok=True)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session by ID"""
        return self._sessions.get(session_id)
    
    def get_current_session(self) -> Optional[SessionInfo]:
        """Get current session"""
        if self.current_session_id:
            return self.get_session(self.current_session_id)
        return None
    
    def set_current_session(self, session_id: str) -> bool:
        """Set current session"""
        if session_id in self._sessions:
            self.current_session_id = session_id
            self.save_sessions()
            return True
        return False
    
    def list_sessions(self) -> List[SessionInfo]:
        """List all sessions"""
        return sorted(self._sessions.values(), key=lambda s: s.updated_at, reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._sessions:
            # Remove session directory
            session_dir = self.get_session_dir(session_id)
            if session_dir.exists():
                import shutil
                shutil.rmtree(session_dir)
            
            # Remove from sessions
            del self._sessions[session_id]
            
            # Update current session if needed
            if self.current_session_id == session_id:
                self.current_session_id = None
                if self._sessions:
                    # Set to most recent session
                    recent_session = max(self._sessions.values(), key=lambda s: s.updated_at)
                    self.current_session_id = recent_session.session_id
            
            self.save_sessions()
            return True
        return False
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session information"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            session.updated_at = datetime.now()
            self.save_sessions()
            return True
        return False
    
    def get_session_dir(self, session_id: str) -> Path:
        """Get session directory path"""
        return self.sessions_dir / session_id
    
    def get_session_memory_file(self, session_id: str) -> Path:
        """Get session memory file path"""
        return self.get_session_dir(session_id) / "memory.json"
    
    def get_session_messages_file(self, session_id: str) -> Path:
        """Get session messages file path"""
        return self.get_session_dir(session_id) / "messages.json"
    
    def increment_message_count(self, session_id: str) -> None:
        """Increment message count for session"""
        if session_id in self._sessions:
            self._sessions[session_id].message_count += 1
            self._sessions[session_id].updated_at = datetime.now()
            self.save_sessions()
    
    def get_or_create_current_session(self) -> str:
        """Get current session or create a new one"""
        if self.current_session_id and self.current_session_id in self._sessions:
            return self.current_session_id
        return self.create_session()
    
    def __len__(self) -> int:
        """Number of sessions"""
        return len(self._sessions)
    
    def __contains__(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self._sessions

