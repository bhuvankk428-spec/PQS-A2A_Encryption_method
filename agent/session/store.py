from agent.session.ticket import SessionTicket


class SessionStore:

    def __init__(self):

        self.tickets = {}

    def save(self, ticket: SessionTicket):

        self.tickets[
            ticket.session_id
        ] = ticket

    def get(self, session_id):

        ticket = self.tickets.get(
            session_id
        )

        if ticket is None:

            return None

        if ticket.expired():

            del self.tickets[
                session_id
            ]

            return None

        return ticket