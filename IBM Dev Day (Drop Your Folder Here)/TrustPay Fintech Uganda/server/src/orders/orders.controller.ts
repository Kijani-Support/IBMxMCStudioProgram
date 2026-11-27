import { Request, Response, NextFunction } from 'express';
import { requireUser } from '../middleware/auth';
import * as ordersService from './orders.service';

export async function create(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const user = requireUser(req);
    const order = await ordersService.createOrder(user.id, req.body);
    res.status(201).json({ order });
  } catch (error) {
    next(error);
  }
}

export async function list(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const user = requireUser(req);
    const orders = await ordersService.listOrders(user.id, user.role);
    res.status(200).json({ orders });
  } catch (error) {
    next(error);
  }
}

export async function getById(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const user = requireUser(req);
    const order = await ordersService.getOrderForUser(req.params.orderId as string, user.id, user.role);
    res.status(200).json({ order });
  } catch (error) {
    next(error);
  }
}

export async function assignRider(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const user = requireUser(req);
    const order = await ordersService.assignRider(req.params.orderId as string, user.id, req.body);
    res.status(200).json({ order });
  } catch (error) {
    next(error);
  }
}
