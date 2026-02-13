const { X402Client } = require('@x402/core');
const { EvmSigner } = require('@x402/evm');
const { ethers } = require('ethers');
require('dotenv').config();

// Configuración de Margen
const MARGIN = 1.20;

class Celer39Economy {
    constructor() {
        this.base_cost_per_token = 0.000001; // Ejemplo: 1 USDC por 1M tokens
    }

    calculatePrice(tokensUsed, computeTimeMs) {
        const directCost = (tokensUsed * this.base_cost_per_token) + (computeTimeMs * 0.00001);
        const finalPrice = directCost * MARGIN;
        return {
            cost: directCost.toFixed(6),
            price: finalPrice.toFixed(6),
            profit: (finalPrice - directCost).toFixed(6)
        };
    }

    async createPaymentRequest(amount, reason) {
        console.log(`[x402] Generando solicitud de pago por ${amount} USDC - Razón: ${reason}`);
        // Integración futura con CDP para generar el invoice on-chain
    }
}

module.exports = new Celer39Economy();
