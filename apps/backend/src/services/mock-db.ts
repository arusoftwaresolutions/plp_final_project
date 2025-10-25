// Mock database for development without PostgreSQL
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
  created_at: Date;
}

interface Household {
  id: number;
  user_id: number;
  household_size: number;
  monthly_income: number;
}

class MockDatabase {
  private users: User[] = [];
  private households: Household[] = [];
  private userIdCounter = 1;
  private householdIdCounter = 1;

  async query(text: string, params: any[] = []) {
    console.log('Mock DB Query:', text.substring(0, 50) + '...', params);
    
    // Handle init-db table existence checks
    if (text.includes('SELECT EXISTS') && text.includes('information_schema.tables')) {
      // Always return false so tables get "created"
      return { rows: [{ exists: false }], rowCount: 1 };
    }
    
    // Handle extension existence checks
    if (text.includes('SELECT EXISTS') && text.includes('pg_extension')) {
      return { rows: [{ exists: false }], rowCount: 1 };
    }
    
    // Handle CREATE TABLE and CREATE EXTENSION statements
    if (text.includes('CREATE TABLE') || text.includes('CREATE EXTENSION')) {
      return { rows: [], rowCount: 0 };
    }
    
    // Handle user registration
    if (text.includes('INSERT INTO users') && text.includes('RETURNING')) {
      const [name, email, password] = params;
      const user: User = { 
        id: this.userIdCounter++, 
        name, 
        email, 
        password,
        created_at: new Date()
      };
      this.users.push(user);
      return { rows: [{ id: user.id, name: user.name, email: user.email }], rowCount: 1 };
    }
    
    // Check if user exists by email
    if (text.includes('SELECT id FROM users WHERE email')) {
      const [email] = params;
      const user = this.users.find(u => u.email === email);
      return { rows: user ? [{ id: user.id }] : [], rowCount: user ? 1 : 0 };
    }
    
    // User login query
    if (text.includes('SELECT id, name, email, password FROM users WHERE email')) {
      const [email] = params;
      const user = this.users.find(u => u.email === email);
      return { rows: user ? [user] : [], rowCount: user ? 1 : 0 };
    }
    
    // Insert household
    if (text.includes('INSERT INTO households') && text.includes('RETURNING')) {
      const [user_id, household_size, monthly_income] = params;
      const household: Household = { 
        id: this.householdIdCounter++, 
        user_id, 
        household_size, 
        monthly_income 
      };
      this.households.push(household);
      return { rows: [household], rowCount: 1 };
    }
    
    // Get household by user ID
    if (text.includes('SELECT id, household_size, monthly_income FROM households WHERE user_id')) {
      const [user_id] = params;
      const household = this.households.find(h => h.user_id === user_id);
      return { rows: household ? [household] : [], rowCount: household ? 1 : 0 };
    }
    
    // Get household with user name for AI (JOIN query)
    if (text.includes('SELECT h.id, h.monthly_income, h.household_size, u.name FROM households h JOIN users u')) {
      const [household_id] = params;
      const household = this.households.find(h => h.id === household_id);
      if (household) {
        const user = this.users.find(u => u.id === household.user_id);
        if (user) {
          const result = {
            id: household.id,
            monthly_income: household.monthly_income,
            household_size: household.household_size,
            name: user.name
          };
          return { rows: [result], rowCount: 1 };
        }
      }
      return { rows: [], rowCount: 0 };
    }
    
    // Get transactions by household ID (for AI)
    if (text.includes('SELECT type, category, amount FROM transactions WHERE household_id')) {
      // Return empty transactions for now since we don't have transaction data in mock
      return { rows: [], rowCount: 0 };
    }

    // Default empty response
    console.log('Unhandled query:', text);
    return { rows: [], rowCount: 0 };
  }

  // Add some sample data for testing
  async addSampleData() {
    console.log('Adding sample data to mock database...');
    // This will be called during initialization
  }
}

export const mockDb = new MockDatabase();