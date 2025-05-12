import { R } from 'build/client/assets/chunk-KNED5TY2-BVPed4it';
import parametersWeights from '../assets/parameters-weights.json';

// ###  LA Update  #########################################################################
export function updateWith_LA(records, la) {
  // Open database connection
  records.forEach((record) => {
    // prepare formal elements
    const monthly_interest_rate = record.interest_rate / (12 * 100);
    const numerator =
      la *
      monthly_interest_rate *
      (1 + monthly_interest_rate) ** record.repayment_duration;
    const denominator =
      (1 + monthly_interest_rate) ** record.repayment_duration - 1;
    // Update loan_amount field
    record.loan_amount = la;
    record.monthly_repayment = numerator / denominator / 10; // change to Toman
    record.deposit_amount = (la / record.loan_coefficient) * 100;
    calculateSortOrder(record);
  });

  const valid_records = records.filter(
    (r) =>
      (r.maximum_deposit_amount === 'nan' ||
        r.deposit_amount <= parseInt(r.maximum_deposit_amount)) &&
      r.loan_amount <= r.loan_amount_limit &&
      r.loan_amount >= r.minimum_loan_amount
  );
  return valid_records;
}
// ###  DA Update  #########################################################################
export function updateWith_DA(records, da) {
  // Open database connection
  records.forEach((record) => {
    let valid_da = // if da is grater than max of deposit amount the
      record.maximum_deposit_amount === 'nan' ||
      da <= parseInt(record.maximum_deposit_amount)
        ? da
        : parseInt(record.maximum_deposit_amount);
    const coefficient = record.loan_coefficient / 100;
    const la = coefficient * valid_da;
    let valid_la = la;
    if (la > record.loan_amount_limit && valid_da < da) {
      valid_la = record.loan_amount_limit;
      valid_da = (valid_la / record.loan_coefficient) * 100;
    }
    // prepare formal elements
    const monthly_interest_rate = record.interest_rate / (12 * 100);
    const numerator =
      valid_la *
      monthly_interest_rate *
      (1 + monthly_interest_rate) ** record.repayment_duration;
    const denominator =
      (1 + monthly_interest_rate) ** record.repayment_duration - 1;
    // Update loan_amount field
    record.loan_amount = valid_la;
    record.monthly_repayment = numerator / denominator / 10;
    record.deposit_amount = valid_da;
    calculateSortOrder(record);
  });

  const valid_records = records.filter(
    (r) =>
      (r.maximum_deposit_amount === 'nan' ||
        r.deposit_amount <= parseInt(r.maximum_deposit_amount)) &&
      r.loan_amount <= r.loan_amount_limit &&
      r.loan_amount >= r.minimum_loan_amount
  );
  return valid_records;
}

// Usage of get data function
// openDatabase().then((db) => getData(db).then((data) => console.log(data)));
// Usage of queryComplex function

// openDatabase().then(db => queryComplex(db).then(matchingRecords => console.log(matchingRecords)));
// openDatabase().then((db) => queryComplex(db));

export function queryComplex(
  scenarios,
  deposit_amount,
  repayment_duration,
  deposit_duration,
  interest_rate,
  credit_score
) {
  const matchingRecords = scenarios.filter((record) => {
    if (
      (deposit_amount ===
        undefined /*record.deposit_amount >= deposit_amount * 10000000 * 0.4 &&*/ ||
        record.deposit_amount <= deposit_amount * 10000000) &&
      (repayment_duration === undefined ||
        record.repayment_duration == repayment_duration) &&
      (deposit_duration === undefined ||
        record.deposit_duration == deposit_duration) &&
      (interest_rate === undefined || record.interest_rate == interest_rate) &&
      (credit_score === undefined ||
        record.credit_score.includes(credit_score) ||
        (credit_score === 'D' && record.credit_score.includes('E')) ||
        (credit_score === 'N' && record.credit_score.includes('فاقد رتبه')))
    ) {
      return true;
    }
    return false;
  });

  return matchingRecords;
}

export function calculateSortOrder(loan) {
  let loanAmountKey = 'out_of_range';
  if (loan.loan_amount <= 500000000) {
    loanAmountKey = '1-50';
  } else if (loan.loan_amount <= 1000000000) {
    loanAmountKey = '50-100';
  } else if (loan.loan_amount <= 1500000000) {
    loanAmountKey = '100-150';
  } else if (loan.loan_amount <= 2000000000) {
    loanAmountKey = '150-200';
  } else if (loan.loan_amount <= 2500000000) {
    loanAmountKey = '200-250';
  } else if (loan.loan_amount <= 3000000000) {
    loanAmountKey = '250-300';
  }

  const ir_value =
    parametersWeights['IR'][loanAmountKey][loan.interest_rate.toString()];
  const rd_value =
    parametersWeights['RD'][loanAmountKey][loan.repayment_duration.toString()];
  const w_type_coef = parametersWeights['w_type'][loanAmountKey][loan.nickname];
  const dd_value = parametersWeights['DD'][loan.deposit_duration.toString()];
  const cs_value =
    parametersWeights['CS'][loan.credit_score.match(/[ABCDE]/)?.[0] ?? 'N'];

  const ir_score = parametersWeights['w']['IR_score'];
  const cs_score = parametersWeights['w']['CS_score'];
  const rd_score = parametersWeights['w']['RD_score'];
  const dd_score = parametersWeights['w']['DD_score'];

  // const w_business = parametersWeights['w_business'][loan.nickname];
  const coef =
    ir_value * ir_score +
    rd_value * rd_score +
    dd_value * dd_score +
    cs_value * cs_score;

  const sortOrder = coef * w_type_coef * loan.loan_coefficient;
  loan.sortOrder = sortOrder;
}
