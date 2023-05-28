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
           String secret16bytes = "MySecretKey12345";

          String encryptedText = encrypt(plainText, secret16bytes);
          System.out.println("Encrypted Text: " + encryptedText);

           String decryptedText = decrypt(encryptedText, secret16bytes);
           System.out.println("Decrypted Text: " + decryptedText);
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

       byte[] combinedBytes = new byte[nonce.length + encryptedBytes.length];
       System.arraycopy(nonce, 0, combinedBytes, 0, nonce.length);
       System.arraycopy(encryptedBytes, 0, combinedBytes, nonce.length, encryptedBytes.length);
       
       System.out.println(combinedBytes.length);

       return Base64.getEncoder().encodeToString(combinedBytes);
   }


   public static String decrypt(String encryptedText, String secret) throws Exception {
       SecretKey secretKey = generateKey(secret);
       Cipher cipher = Cipher.getInstance(ENCRYPTION_ALGORITHM);

       byte[] combinedBytes = Base64.getDecoder().decode(encryptedText);
       
       System.out.println(combinedBytes.length);
       
       byte[] nonce = new byte[GCM_NONCE_LENGTH];
       byte[] encryptedBytes = new byte[combinedBytes.length - GCM_NONCE_LENGTH];

       System.arraycopy(combinedBytes, 0, nonce, 0, GCM_NONCE_LENGTH);
       System.arraycopy(combinedBytes, GCM_NONCE_LENGTH, encryptedBytes, 0, encryptedBytes.length);

       GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, nonce);
       cipher.init(Cipher.DECRYPT_MODE, secretKey, parameterSpec);

       byte[] decryptedBytes = cipher.doFinal(encryptedBytes);

       return new String(decryptedBytes, StandardCharsets.UTF_8);
   }

   private static SecretKey generateKey(String secret) throws Exception {
       byte[] secretBytes = secret.getBytes(StandardCharsets.UTF_8);
       SecretKeySpec secretKeySpec = new SecretKeySpec(secretBytes, "AES");
       return secretKeySpec;
   }

   private static byte[] generateNonce() {
       byte[] nonce = new byte[GCM_NONCE_LENGTH];
       SecureRandom secureRandom = new SecureRandom();
       secureRandom.nextBytes(nonce);
       return nonce;
   }
}

