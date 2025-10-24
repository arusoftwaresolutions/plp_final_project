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
      return { rows: [{ exists: false }] };
    }
    
    // Handle extension existence checks
    if (text.includes('SELECT EXISTS') && text.includes('pg_extension')) {
      return { rows: [{ exists: false }] };
    }
    
    // Handle CREATE TABLE and CREATE EXTENSION statements
    if (text.includes('CREATE TABLE') || text.includes('CREATE EXTENSION')) {
      return { rows: [] };
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
      return { rows: [{ id: user.id, name: user.name, email: user.email }] };
    }
    
    // Check if user exists by email
    if (text.includes('SELECT id FROM users WHERE email')) {
      const [email] = params;
      const user = this.users.find(u => u.email === email);
      return { rows: user ? [{ id: user.id }] : [] };
    }
    
    // User login query
    if (text.includes('SELECT id, name, email, password FROM users WHERE email')) {
      const [email] = params;
      const user = this.users.find(u => u.email === email);
      return { rows: user ? [user] : [] };
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
      return { rows: [household] };
    }
    
    // Get household by user ID
    if (text.includes('SELECT id, household_size, monthly_income FROM households WHERE user_id')) {
      const [user_id] = params;
      const household = this.households.find(h => h.user_id === user_id);
      return { rows: household ? [household] : [] };
    }

    // Default empty response
    console.log('Unhandled query:', text);
    return { rows: [] };
  }

  // Add some sample data for testing
  async addSampleData() {
    console.log('Adding sample data to mock database...');
    // This will be called during initialization
  }
}

export const mockDb = new MockDatabase();