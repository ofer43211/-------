# Shared Packages Guide

## Overview

In a monorepo, you often have code that's shared across multiple projects. This guide shows how to create and use shared packages.

## Creating a Shared Package

### Example: Shared Utilities

Let's create a shared utilities package that all projects can use:

```bash
# Create the package directory
mkdir -p packages/shared/utils

# Navigate to it
cd packages/shared/utils
```

### Create package.json

```json
{
  "name": "@unified/utils",
  "version": "1.0.0",
  "description": "Shared utilities for all projects",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "test": "jest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
```

### Create TypeScript Config

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### Create Source Files

```typescript
// src/index.ts
export * from './logger';
export * from './validators';
export * from './formatters';

// src/logger.ts
export class Logger {
  static info(message: string) {
    console.log(`[INFO] ${new Date().toISOString()}: ${message}`);
  }

  static error(message: string) {
    console.error(`[ERROR] ${new Date().toISOString()}: ${message}`);
  }

  static warn(message: string) {
    console.warn(`[WARN] ${new Date().toISOString()}: ${message}`);
  }
}

// src/validators.ts
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// src/formatters.ts
export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(amount);
}
```

## Using the Shared Package

### In Another Project

```bash
# In packages/rotem/rotem_brain/package.json
{
  "dependencies": {
    "@unified/utils": "workspace:*"
  }
}
```

### Import and Use

```typescript
// In packages/rotem/rotem_brain/src/app.ts
import { Logger, isValidEmail, formatDate } from '@unified/utils';

Logger.info('Application started');

const email = 'user@example.com';
if (isValidEmail(email)) {
  Logger.info(`Valid email: ${email}`);
}

const today = formatDate(new Date());
Logger.info(`Today is: ${today}`);
```

## Common Shared Packages

### 1. Shared Types

```typescript
// packages/shared/types/src/index.ts

export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export type Role = 'admin' | 'user' | 'guest';
```

### 2. Shared Configuration

```typescript
// packages/shared/config/src/index.ts

export const config = {
  api: {
    baseUrl: process.env.API_BASE_URL || 'http://localhost:3000',
    timeout: 30000
  },
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432')
  },
  features: {
    enableAnalytics: process.env.ENABLE_ANALYTICS === 'true',
    enableLogging: process.env.ENABLE_LOGGING !== 'false'
  }
};
```

### 3. Shared Components (React)

```typescript
// packages/shared/ui/src/Button.tsx

import React from 'react';

export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  disabled = false
}) => {
  const baseClasses = 'px-4 py-2 rounded font-medium transition';
  const variantClasses = {
    primary: 'bg-blue-500 hover:bg-blue-600 text-white',
    secondary: 'bg-gray-500 hover:bg-gray-600 text-white',
    danger: 'bg-red-500 hover:bg-red-600 text-white'
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
```

### 4. Shared API Client

```typescript
// packages/shared/api-client/src/index.ts

export class ApiClient {
  constructor(private baseUrl: string) {}

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }
}
```

## Workspace Configuration

Update root `package.json` to include shared packages:

```json
{
  "workspaces": [
    "packages/rotem/*",
    "packages/gemini/*",
    "packages/ai-platforms/*",
    "packages/tools/*",
    "packages/infrastructure/*",
    "packages/shared/*"
  ]
}
```

## Building Shared Packages

### Build Order

Turbo automatically handles build order. Update `turbo.json`:

```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

This ensures shared packages build before packages that depend on them.

### Build Command

```bash
# Build all packages (shared packages build first)
npm run build:all
```

## Best Practices

### 1. Versioning

Use `workspace:*` for internal dependencies:

```json
{
  "dependencies": {
    "@unified/utils": "workspace:*",
    "@unified/types": "workspace:*"
  }
}
```

### 2. Naming Convention

Use a scoped package name:
- `@unified/utils`
- `@unified/types`
- `@unified/config`

### 3. Keep Them Small

Each shared package should have a single responsibility:
- ✅ `@unified/logger` - just logging
- ✅ `@unified/validators` - just validation
- ❌ `@unified/everything` - too broad

### 4. Document Thoroughly

Each shared package should have:
- Clear README.md
- TypeScript types
- Usage examples
- Changelog

### 5. Test Shared Code

Shared code is used everywhere, so test it well:

```typescript
// packages/shared/utils/src/__tests__/validators.test.ts

import { isValidEmail } from '../validators';

describe('isValidEmail', () => {
  it('should validate correct emails', () => {
    expect(isValidEmail('user@example.com')).toBe(true);
  });

  it('should reject invalid emails', () => {
    expect(isValidEmail('not-an-email')).toBe(false);
  });
});
```

## Example: Creating Shared Constants

```bash
# Create package
mkdir -p packages/shared/constants/src
cd packages/shared/constants

# Create package.json
cat > package.json << 'EOF'
{
  "name": "@unified/constants",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc"
  }
}
EOF

# Create source
cat > src/index.ts << 'EOF'
export const API_ENDPOINTS = {
  USERS: '/api/users',
  AUTH: '/api/auth',
  PROJECTS: '/api/projects'
};

export const ERROR_MESSAGES = {
  UNAUTHORIZED: 'You are not authorized to perform this action',
  NOT_FOUND: 'Resource not found',
  SERVER_ERROR: 'An internal server error occurred'
};

export const ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  GUEST: 'guest'
} as const;
EOF

# Build
npm run build
```

## Using in Projects

```typescript
// In any project
import { API_ENDPOINTS, ERROR_MESSAGES, ROLES } from '@unified/constants';

// Use them
fetch(API_ENDPOINTS.USERS);
console.error(ERROR_MESSAGES.UNAUTHORIZED);
const isAdmin = user.role === ROLES.ADMIN;
```

## Benefits of Shared Packages

1. **DRY Principle**: Write once, use everywhere
2. **Consistency**: Same behavior across all projects
3. **Maintainability**: Fix bugs in one place
4. **Type Safety**: Shared TypeScript types
5. **Version Control**: Single source of truth

---

**Ready to create shared packages?** Start small with utilities and grow from there!
