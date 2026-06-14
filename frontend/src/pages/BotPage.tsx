import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { botAPI } from '@/lib/api'

interface BotConfig {
    token: string
    admin_id: number
    is_active: boolean
}

export function BotPage() {
    const [botConfig, setBotConfig] = useState<BotConfig>({
        token: '',
        admin_id: 0,
        is_active: false,
    })

    const [loading, setLoading] = useState(false)

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const config = await botAPI.getBotConfig()

                setBotConfig({
                    token: config.token || '',
                    admin_id: Number(config.admin_id) || 0,
                    is_active: Boolean(config.is_active),
                })
            } catch (error) {
                console.error(error)
                alert('Failed to fetch bot config')
            }
        }

        fetchConfig()
    }, [])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            await botAPI.updateBotConfig({
                token: botConfig.token,
                admin_id: Number(botConfig.admin_id),
                is_active: botConfig.is_active,
            })

            alert('Bot settings updated successfully')
        } catch (error) {
            console.error(error)
            alert('Failed to update bot settings')
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target

        setBotConfig(prev => ({
            ...prev,
            [name]: name === 'admin_id' ? Number(value) : value,
        }))
    }

    return (
        <div className="mx-auto w-full max-w-5xl p-6 space-y-6">
            <div>
                <h1 className="text-3xl font-bold">
                    Bot Management
                </h1>

                <p className="text-muted-foreground mt-1">
                    Configure and manage Telegram bot settings
                </p>
            </div>

            <form
                onSubmit={handleSubmit}
                className="grid gap-6 md:grid-cols-2"
            >
                {/* Settings Card */}
                <div className="rounded-xl border bg-card p-6 shadow-sm space-y-5">
                    <div>
                        <h2 className="font-semibold text-lg">
                            Bot Settings
                        </h2>

                        <p className="text-sm text-muted-foreground">
                            Configure bot credentials
                        </p>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">
                            Bot Token
                        </label>

                        <Input
                            name="token"
                            value={botConfig.token}
                            onChange={handleChange}
                            placeholder="Enter bot token"
                            required
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">
                            Admin ID
                        </label>

                        <Input
                            name="admin_id"
                            type="number"
                            value={botConfig.admin_id}
                            onChange={handleChange}
                            placeholder="Enter admin ID"
                            required
                        />
                    </div>
                </div>

                {/* Status Card */}
                <div className="rounded-xl border bg-card p-6 shadow-sm">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="font-semibold text-lg">
                                Bot Status
                            </h2>

                            <p className="text-sm text-muted-foreground mt-1">
                                Enable or disable Telegram bot
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() =>
                                setBotConfig(prev => ({
                                    ...prev,
                                    is_active: !prev.is_active,
                                }))
                            }
                            className={`relative h-8 w-16 rounded-full transition-all duration-300 ${botConfig.is_active
                                    ? 'bg-green-500'
                                    : 'bg-red-500'
                                }`}
                        >
                            <span
                                className={`absolute top-1 h-6 w-6 rounded-full bg-white shadow transition-transform duration-300 ${botConfig.is_active
                                        ? 'translate-x-9'
                                        : 'translate-x-1'
                                    }`}
                            />
                        </button>
                    </div>

                    <div className="mt-6">
                        <span
                            className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${botConfig.is_active
                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                    : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                }`}
                        >
                            {botConfig.is_active
                                ? '🟢 Active'
                                : '🔴 Inactive'}
                        </span>
                    </div>
                </div>

                {/* Save Button */}
                <div className="md:col-span-2 flex justify-end">
                    <Button
                        type="submit"
                        disabled={loading}
                        size="lg"
                    >
                        {loading
                            ? 'Saving...'
                            : 'Save Changes'}
                    </Button>
                </div>
            </form>
        </div>
    )
}