/**
 * FREE WhatsApp Ticketing Bot
 * Uses whatsapp-web.js (Open Source - No API costs!)
 * Connects to Python backend for AI processing
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
require('dotenv').config();

// Configuration
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:5000';
const WHITELIST_FILE = process.env.WHITELIST_FILE || 'config/whitelist.json';

// Load whitelist with better error handling
const fs = require('fs');
let whitelist = [];
let whitelistEnabled = false;

try {
    if (fs.existsSync(WHITELIST_FILE)) {
        const whitelistData = fs.readFileSync(WHITELIST_FILE, 'utf8');
        const parsed = JSON.parse(whitelistData);
        
        // Support both 'allowed_numbers' and 'whitelisted_numbers'
        whitelist = parsed.allowed_numbers || parsed.whitelisted_numbers || [];
        
        // Remove any + or spaces from numbers
        whitelist = whitelist.map(num => num.replace(/[\s+]/g, ''));
        
        whitelistEnabled = whitelist.length > 0;
        console.log(`✅ Loaded ${whitelist.length} whitelisted numbers`);
        if (whitelistEnabled) {
            console.log(`🔒 Whitelist ENABLED - only these numbers can create tickets:`);
            whitelist.forEach(num => console.log(`   • ${num}`));
        } else {
            console.log(`⚠️  Whitelist is empty - allowing ALL numbers`);
        }
    } else {
        console.warn(`⚠️  Whitelist file not found: ${WHITELIST_FILE}`);
        console.warn(`⚠️  Allowing ALL numbers (no whitelist)`);
    }
} catch (error) {
    console.warn(`⚠️  Error loading whitelist: ${error.message}`);
    console.warn(`⚠️  Allowing ALL numbers (no whitelist)`);
}

// Initialize WhatsApp client with persistent session
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: '.wa_session'
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// QR Code for first-time authentication
client.on('qr', (qr) => {
    console.log('\n📱 Scan this QR code with WhatsApp on your phone:\n');
    qrcode.generate(qr, { small: true });
    console.log('\nAfter scanning, the session will be saved locally.');
});

// Client ready
client.on('ready', () => {
    console.log('\n✅ WhatsApp Bot is ready!');
    console.log('📞 Listening for messages...\n');
});

// Handle authentication
client.on('authenticated', () => {
    console.log('✅ Authenticated successfully!');
});

client.on('auth_failure', (msg) => {
    console.error('❌ Authentication failed:', msg);
});

// Message handler
client.on('message', async (message) => {
    try {
        // Skip own messages immediately
        if (message.fromMe) {
            return;
        }
        
        // Skip group messages immediately
        if (message.from.includes('@g.us')) {
            return;
        }
        
        // Skip WhatsApp channels/lists
        if (message.from.includes('@lid')) {
            return;
        }
        
        // Skip empty messages
        if (!message.body || message.body.trim() === '') {
            return;
        }
        
        const senderNumber = message.from.replace('@c.us', '').replace('@s.whatsapp.net', '');
        const senderName = (await message.getContact()).pushname || 'User';
        
        // Whitelist check (only if whitelist is enabled) - SILENT rejection
        if (whitelistEnabled && !whitelist.includes(senderNumber)) {
            console.log(`🚫 Silently ignored: ${senderNumber} not in whitelist`);
            return; // Just ignore, no reply
        }
        
        console.log(`\n📨 Message from ${senderName} (${senderNumber}):`);
        console.log(`   "${message.body}"`);
        
        // Process message through Python backend
        console.log('🤖 Processing with AI...');
        
        const response = await axios.post(`${PYTHON_BACKEND_URL}/process`, {
            message: message.body,
            user_number: senderNumber,
            user_name: senderName
        }, {
            timeout: 30000 // 30 second timeout
        });
        
        const result = response.data;
        
        // Send response back to user
        if (result.reply) {
            await message.reply(result.reply);
            console.log(`✅ Sent reply: "${result.reply.substring(0, 50)}..."`);
        }
        
    } catch (error) {
        console.error('❌ Error processing message:', error.message);
        
        // Check if it's a backend connection error
        if (error.code === 'ECONNREFUSED' || error.message.includes('ECONNREFUSED')) {
            console.error('❌ Python backend is not running! Start it with: python3 src/webhook/whatsapp_handler.py');
            try {
                await message.reply('⚠️ Bot backend is currently unavailable. Please contact the administrator.');
            } catch (replyError) {
                // Ignore reply errors
            }
        } else {
            // Other errors - send generic message to user
            try {
                await message.reply('⚠️ Sorry, I encountered an error processing your request. Please try again later.');
            } catch (replyError) {
                console.error('❌ Could not send error reply:', replyError.message);
            }
        }
    }
});

// Disconnection handler
client.on('disconnected', (reason) => {
    console.log('⚠️ Client was disconnected:', reason);
    console.log('Attempting to reconnect...');
});

// Handle process termination
process.on('SIGINT', async () => {
    console.log('\n\n🛑 Shutting down gracefully...');
    await client.destroy();
    process.exit(0);
});

// Check if Python backend is running on startup
console.log('🚀 Starting FREE WhatsApp Ticketing Bot...');
console.log('💡 Using open-source whatsapp-web.js - No API costs!');
console.log(`🔗 Python backend: ${PYTHON_BACKEND_URL}`);

// Test backend connection
axios.get(`${PYTHON_BACKEND_URL}/health`)
    .then(response => {
        console.log('✅ Python backend is running');
        console.log(`   Version: ${response.data.version || 'FREE'}`);
        console.log(`   AI: ${response.data.ai_provider || 'Groq'}`);
    })
    .catch(error => {
        console.warn('⚠️  Python backend is NOT running!');
        console.warn('   Start it with: python3 src/webhook/whatsapp_handler.py');
        console.warn('   Bot will wait for backend to start...');
    });

console.log('');
client.initialize();
