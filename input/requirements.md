# Raw requirements (from the event organiser, unedited)

We're running a tech conference and need the registration form to reject bad data
before it hits our database.

- People must give their full name (at least 2 characters, max 60).
- Email is required and has to look like a real email.
- Age is required, must be a whole number, and attendees must be between 16 and 120.
- Ticket type is one of: standard, vip, student.
- If someone picks a student ticket they MUST give a student ID, which looks like
  STU followed by 6 digits (e.g. STU123456).
- Promo codes are optional. If given, they are 5–10 uppercase letters/digits.
- VIP tickets can't be combined with a promo code.
- We want ALL problems reported at once, not just the first one.
