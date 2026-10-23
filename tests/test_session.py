from agent.session.manager import SessionManager

manager = SessionManager()

# New session
session1 = manager.create()

print(session1.session_id)

# Restore same session
session2 = manager.get_or_create(session1.session_id)

print(session2.session_id)

print(session1 is session2)

print(manager.count())