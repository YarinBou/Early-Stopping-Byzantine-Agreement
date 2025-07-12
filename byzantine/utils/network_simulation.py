class Party:
    def __init__(self, party_id, n, t):
        self.party_id = party_id
        self.n = n
        self.t = t
        self.message_queue = []

    def send(self, message, recipients):
        for recipient in recipients:
            recipient.receive(message)

    def receive(self, message):
        self.message_queue.append(message)

    def process_round(self):
        # Process all messages in this round
        messages = self.message_queue
        self.message_queue = []
        return messages
