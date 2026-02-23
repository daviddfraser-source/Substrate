import type { PrismaClient } from "@prisma/client";

export interface DatabaseAdapter {
  client: PrismaClient;
  getItems(limit?: number): Promise<{ id: string; title: string; description: string }[]>;
}

export class PrismaAdapter implements DatabaseAdapter {
  constructor(public client: PrismaClient) {}

  async getItems(limit = 10) {
    return this.client.item.findMany({
      take: limit,
      orderBy: { createdAt: "desc" }
    });
  }
}

export function createAdapter(client: PrismaClient): DatabaseAdapter {
  return new PrismaAdapter(client);
}
