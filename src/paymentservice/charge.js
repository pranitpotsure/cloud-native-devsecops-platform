// PaymentService - Realistic Payment Simulation
// Simulates a real payment gateway (Razorpay-style) with:
//   - Luhn algorithm card validation
//   - VISA / MasterCard acceptance
//   - Expiry validation
//   - Realistic transaction IDs (pay_XXXXXXXXXX format)
//   - Proper error messages matching real gateway responses

const { v4: uuidv4 } = require('uuid');
const pino = require('pino');

const logger = pino({
  name: 'paymentservice-charge',
  messageKey: 'message',
  formatters: {
    level(logLevelString) {
      return { severity: logLevelString };
    }
  }
});

// ─── Error Classes ────────────────────────────────────────────────────────────

class CreditCardError extends Error {
  constructor(message) {
    super(message);
    this.code = 400;
  }
}

class InvalidCreditCard extends CreditCardError {
  constructor() {
    super('Your card number is invalid. Please check the number and try again.');
  }
}

class UnacceptedCreditCard extends CreditCardError {
  constructor(cardType) {
    super(`Sorry, we do not accept ${cardType} cards. Please use VISA or Mastercard.`);
  }
}

class ExpiredCreditCard extends CreditCardError {
  constructor(number, month, year) {
    super(`Your card ending in ${number.slice(-4)} expired on ${String(month).padStart(2,'0')}/${year}. Please use a valid card.`);
  }
}

// ─── Luhn Algorithm (real card number validation) ─────────────────────────────

function luhnCheck(cardNumber) {
  const digits = cardNumber.replace(/\D/g, '');
  if (digits.length < 13 || digits.length > 19) return false;

  let sum = 0;
  let isEven = false;
  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10);
    if (isEven) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    sum += digit;
    isEven = !isEven;
  }
  return sum % 10 === 0;
}

// ─── Card Type Detection ──────────────────────────────────────────────────────

function detectCardType(cardNumber) {
  const num = cardNumber.replace(/\D/g, '');
  if (/^4/.test(num)) return 'visa';
  if (/^5[1-5]/.test(num) || /^2(2[2-9][1-9]|[3-6]\d{2}|7([01]\d|20))/.test(num)) return 'mastercard';
  if (/^3[47]/.test(num)) return 'amex';
  if (/^6(?:011|5)/.test(num)) return 'discover';
  if (/^3(?:0[0-5]|[68])/.test(num)) return 'diners';
  return 'unknown';
}

// ─── Realistic Transaction ID (Razorpay-style) ────────────────────────────────

function generateTransactionId() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = 'pay_';
  for (let i = 0; i < 16; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// ─── Main Charge Function ─────────────────────────────────────────────────────

module.exports = function charge(request) {
  const { amount, credit_card: creditCard } = request;
  const rawNumber = creditCard.credit_card_number;
  const cardNumber = rawNumber.replace(/[\s\-]/g, '');

  // Step 1: Luhn check
  if (!luhnCheck(cardNumber)) {
    throw new InvalidCreditCard();
  }

  // Step 2: Card type check
  const cardType = detectCardType(cardNumber);
  if (cardType !== 'visa' && cardType !== 'mastercard') {
    const displayType = cardType.charAt(0).toUpperCase() + cardType.slice(1);
    throw new UnacceptedCreditCard(displayType === 'Unknown' ? 'this type of' : displayType);
  }

  // Step 3: Expiry check
  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();
  const { credit_card_expiration_year: year, credit_card_expiration_month: month } = creditCard;
  if ((currentYear * 12 + currentMonth) > (year * 12 + month)) {
    throw new ExpiredCreditCard(cardNumber, month, year);
  }

  // Step 4: Generate realistic transaction ID
  const transactionId = generateTransactionId();

  logger.info({
    message: 'Payment processed successfully',
    card_type: cardType.toUpperCase(),
    card_last4: cardNumber.slice(-4),
    amount: `${amount.currency_code} ${amount.units}.${String(amount.nanos).padStart(9, '0').slice(0, 2)}`,
    transaction_id: transactionId
  });

  return { transaction_id: transactionId };
};
