// Test binary with RSA encryption for PQC Inspector
// Compile: gcc -o test_crypto_binary test_crypto_binary.c -lcrypto -lssl

#include <stdio.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/err.h>

int main() {
    printf("Testing RSA encryption (Non-PQC)...\n");

    // Generate RSA key pair
    RSA *rsa = RSA_new();
    BIGNUM *e = BN_new();

    BN_set_word(e, RSA_F4);
    RSA_generate_key_ex(rsa, 2048, e, NULL);

    printf("RSA 2048-bit key generated successfully!\n");

    // Cleanup
    RSA_free(rsa);
    BN_free(e);

    return 0;
}
