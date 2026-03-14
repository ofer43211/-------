export class Logger {
  constructor(private prefix: string = '') {}

  private format(level: string, message: string): string {
    const timestamp = new Date().toISOString();
    const tag = this.prefix ? `[${this.prefix}] ` : '';
    return `[${level}] ${timestamp}: ${tag}${message}`;
  }

  info(message: string): void {
    console.log(this.format('INFO', message));
  }

  error(message: string): void {
    console.error(this.format('ERROR', message));
  }

  warn(message: string): void {
    console.warn(this.format('WARN', message));
  }

  debug(message: string): void {
    if (process.env.DEBUG) {
      console.debug(this.format('DEBUG', message));
    }
  }
}
