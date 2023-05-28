import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Base64;

public class Aes {
   private static final int GCM_NONCE_LENGTH = 12;
   private static final int GCM_TAG_LENGTH = 16;
   private static final String ENCRYPTION_ALGORITHM = "AES/GCM/NoPadding";

   public static void main(String[] args) {
       try {
           String plainText = "1700612387";
           String secret16bytes = "My*********12345";

           String encryptedText = encrypt(plainText, secret16bytes);
           System.out.println("Encrypted Text: " + encryptedText);
       } catch (Exception e) {
           e.printStackTrace();
       }
   }

   public static String encrypt(String plainText, String secret) throws Exception {
       SecretKey secretKey = generateKey(secret);
       Cipher cipher = Cipher.getInstance(ENCRYPTION_ALGORITHM);

       byte[] nonce = generateNonce();
       GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, nonce);
       cipher.init(Cipher.ENCRYPT_MODE, secretKey, parameterSpec);

       byte[] encryptedBytes = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));

       // block:start:nonce-combined-plaintext
       byte[] combinedBytes = new byte[nonce.length + encryptedBytes.length];
       System.arraycopy(nonce, 0, combinedBytes, 0, nonce.length);
       System.arraycopy(encryptedBytes, 0, combinedBytes, nonce.length, encryptedBytes.length);
       // block:end:nonce-combined-plaintext

       // block:start:base64-encode-encrypt
       return Base64.getEncoder().encodeToString(combinedBytes);
       // block:end:base64-encode-encrypt
   }

   // block:start:read-secret-key
   private static SecretKey generateKey(String secret) throws Exception {
       byte[] secretBytes = secret.getBytes(StandardCharsets.UTF_8);
       SecretKeySpec secretKeySpec = new SecretKeySpec(secretBytes, "AES");
       return secretKeySpec;
   }
   // block:end:read-secret-key

   // block:start:generate-nonce
   private static byte[] generateNonce() {
       byte[] nonce = new byte[GCM_NONCE_LENGTH];
       SecureRandom secureRandom = new SecureRandom();
       secureRandom.nextBytes(nonce);
       return nonce;
   }
   // block:end:generate-nonce
}