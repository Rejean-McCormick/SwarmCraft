export interface User {
  id: string;
  username?: string;
  balance: number;
  created_at?: string;
}

export interface Item {
  id: string;
  name: string;
  price: number;
  description?: string;
}
