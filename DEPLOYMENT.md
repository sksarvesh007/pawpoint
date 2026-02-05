# PawPoint Deployment Guide (Free Tier)

Deploy your backend and voice services for free using Render, Neon, and LiveKit Cloud.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Vercel (FE)    │────▶│  Render (API)   │────▶│  Neon (Postgres)│
│  pawpoint-psi   │     │  pawpoint-api   │     │  Free 0.5GB     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  LiveKit Cloud  │◀──── pawpoint-livekit-agent
                        │  (Voice/WebRTC) │      (Render Worker)
                        └─────────────────┘
```

## Step 1: Create Neon PostgreSQL Database

1. Go to https://neon.tech and sign up (free)
2. Create a new project: `pawpoint`
3. Copy the connection string (looks like):
   ```
   postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Important**: Change `postgresql://` to `postgresql+asyncpg://` for SQLAlchemy:
   ```
   postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

## Step 2: Create Redis Instance (Upstash - Free)

1. Go to https://upstash.com and sign up (free)
2. Create a new Redis database
3. Select the **US East** region (closest to Render)
4. Copy the connection string (REST URL with password)
   - Format: `redis://default:PASSWORD@HOST:PORT`

## Step 3: Set Up LiveKit Cloud

1. Go to https://cloud.livekit.io and sign up (free)
2. Create a new project: `pawpoint`
3. Copy these values from Settings → Keys:
   - `LIVEKIT_API_KEY` (starts with `API`)
   - `LIVEKIT_API_SECRET`
   - `LIVEKIT_URL` (e.g., `wss://pawpoint-xxxxx.livekit.cloud`)

## Step 4: Deploy Backend to Render

1. Go to https://render.com and sign up (free)
2. Click **New** → **Blueprint**
3. Connect your GitHub repo: `sksarvesh007/pawpoint`
4. Select the `VET-36` branch (or merge to `main` first)
5. Render will detect `render.yaml` automatically
6. Set the environment variables when prompted:

   | Variable | Value |
   |----------|-------|
   | `DATABASE_URL` | Your Neon connection string (with `+asyncpg`) |
   | `REDIS_URL` | Your Upstash Redis connection string |
   | `LIVEKIT_API_KEY` | From LiveKit Cloud |
   | `LIVEKIT_API_SECRET` | From LiveKit Cloud |
   | `LIVEKIT_URL` | From LiveKit Cloud (wss://...) |
   | `DEEPSEEK_API_KEY` | Your DeepSeek API key |
   | `ASSEMBLYAI_API_KEY` | (Optional) For speech-to-text |
   | `CARTESIA_API_KEY` | (Optional) For text-to-speech |

7. Click **Apply** to deploy

**Note**: DeepSeek base URL and model are pre-configured in render.yaml. You only need to provide your API key.

## Step 5: Run Database Migrations

After deployment, run migrations via Render Shell:

1. Go to your `pawpoint-api` service on Render
2. Click **Shell** tab
3. Run:
   ```bash
   uv run alembic upgrade head
   ```

Or locally (if you have access to production DB):
```bash
DATABASE_URL="your-neon-url" uv run alembic upgrade head
```

## Step 6: Update Vercel Frontend

Add these environment variables in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://pawpoint-api.onrender.com` |
| `API_URL` | `https://pawpoint-api.onrender.com` |
| `NEXT_PUBLIC_LIVEKIT_WS_URL` | Your LiveKit Cloud WSS URL |

Then redeploy:
```bash
vercel --prod
```

Or trigger a redeploy from Vercel dashboard.

## Service URLs

After deployment, your services will be at:

| Service | URL |
|---------|-----|
| Frontend | https://pawpoint-psi.vercel.app |
| Backend API | https://pawpoint-api.onrender.com |
| API Docs | https://pawpoint-api.onrender.com/docs |
| Health Check | https://pawpoint-api.onrender.com/health |

## Free Tier Limitations

| Service | Limit | Impact |
|---------|-------|--------|
| **Render Web** | Spins down after 15 min inactivity | First request may take 30-60s |
| **Render Worker** | 750 hours/month | Should be enough for testing |
| **Neon** | 0.5 GB storage | Plenty for development |
| **LiveKit Cloud** | 50 participant-mins/month | ~50 voice calls |

## Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify `DATABASE_URL` has `+asyncpg` in it
- Ensure all required env vars are set

### Database connection fails
- Neon free tier may pause after inactivity
- First connection may take a few seconds to wake up
- Check Neon dashboard for connection issues

### Voice not working
- Verify LiveKit credentials are correct
- Check browser console for WebSocket errors
- Ensure `NEXT_PUBLIC_LIVEKIT_WS_URL` is set in Vercel

### CORS errors
- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Must be exact match (no trailing slash)

## Seeding Data (Optional)

To seed test data, use Render Shell:

```bash
PYTHONPATH=. uv run python scripts/seed_data.py --minimal
```

## Local Development with Production DB

If you need to test locally against production database:

```bash
# In backend directory
export DATABASE_URL="postgresql+asyncpg://..."
PYTHONPATH=. uv run fastapi dev app/main.py
```

⚠️ Be careful not to corrupt production data!
