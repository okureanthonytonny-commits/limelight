# Limelight MVP – Development Issues

## Issue 1: Project setup and environment
- [x] Initialize backend (FastAPI) and frontends (Vite + React) if not done.
- [x] Add `.env.example` with placeholders for database URL, OAuth keys.
- [x] Configure Pydantic settings in `backend/config.py`.
- [x] Set up PostgreSQL locally or use a free cloud tier (Neon, Supabase).
- [x] Ensure Alembic is configured correctly (single `alembic` folder).

## Issue 2: Session‑based authentication with OAuth
- [x] Implement OAuth (Google) login using `authlib`.
- [x] Create `users` table with `role` column (default 'customer').
- [x] Create `sessions` table (session_id, user_id, expires_at).
- [x] Build login endpoint that sets HttpOnly cookie.
- [x] Create dependency `get_current_user` in `dependencies.py`.
- [x] Create `require_admin` dependency for admin routes.
- [x] Protect store routes with `get_current_user`.

## Issue 3: Product management (admin) and listing (store)
- [x] Create `products` table (name, description, price, stock, image_url).
- [x] Admin endpoints: CRUD for products.
- [x] Store endpoints: public product list and detail.
- [x] Admin frontend: product form with image compression (`browser-image-compression`).
- [x] Store frontend: product cards and detail page.

## Issue 4: Cart functionality (backend persistence + frontend state)
- [x] Create `cart_items` table (user_id, product_id, quantity).
- [x] Backend cart endpoints: get, add/update, remove.
- [x] Store frontend: cart context/reducer with localStorage fallback.
- [x] Sync cart with backend on login and after actions.

## Issue 5: Order placement and order history
- [x] 5.1 Add `role` field to User model and enforce admin via `require_admin` dependency.
- [x] 5.2 Add `stock` validation to cart endpoint behaviors.
- [x] 5.3 Create `OrderItem` model and matching migrations (phase 2, complete).
- [x] 5.4 Implement order creation endpoint `POST /store/orders`, clear cart.
- [x] 5.5 Add order history for customers and admin order management endpoints.
- [x] 5.6 Add follow-up from cart/product: stock validation in cart, stock decrement on order placement.
- [x] 5.7 Add admin order status update and order-item snapshots.

## Issue 6: Admin hero section management
- [ ] Create hero storage (table or settings JSON).
- [ ] Admin endpoints: `GET /admin/hero`, `PUT /admin/hero`.
- [ ] Public endpoint: `GET /store/hero`.
- [ ] Admin frontend: form to edit hero with image upload.

## Issue 7: Error handling and user‑friendly fallbacks
- [ ] Add global exception handlers in FastAPI for consistent JSON errors.
- [ ] Create simple static error pages (404, 500) for frontend.
- [ ] Frontend error boundaries and toast notifications for API errors.

## Issue 8: Testing – backend and frontend
- [ ] Write pytest tests for critical backend endpoints.
- [ ] Write Vitest tests for frontend components (cart, forms).
- [ ] (Optional) Playwright test for full checkout flow.

## Issue 9: Deployment preparation
- [ ] Set up Vercel projects for both frontends.
- [ ] Set up Render Web Service for backend with PostgreSQL.
- [ ] Configure environment variables on hosting platforms.
- [ ] Switch image storage to Cloudinary (free tier) for production.
- [ ] Update API URLs in frontend builds.

## Issue 10: Final MVP integration and manual testing
- [ ] Run through all user stories as customer and admin.
- [ ] Verify session persistence, role enforcement, data consistency.
- [ ] Fix UX/UI glitches.
- [ ] Prepare demo or handover.
