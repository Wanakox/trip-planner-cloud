import { httpClient } from './http'

export type Currency = {
  code: string
  name: string
}

export type CurrencyConversion = {
  amount: string
  from_currency: string
  to_currency: string
  rate: string
  result: string
  rate_date: string
}

export async function getCurrencies(): Promise<Currency[]> {
  const { data } = await httpClient.get<Currency[]>('/currencies')
  return data
}

export async function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string,
): Promise<CurrencyConversion> {
  const { data } = await httpClient.get<CurrencyConversion>('/currencies/convert', {
    params: {
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency,
    },
  })
  return data
}
