/**
 * Government Integrations Services
 *
 * Exports de todos os services de integrações governamentais
 */

export * from './receita-federal.service';
export * from './nfse.service';
export * from './esocial.service';
export * from './sefaz.service';
export * from './sped.service';
export * from './fgts-simples.service';
export * from './govbr-ecac.service';
export * from './sync-certificates.service';

export { default as receitaFederalService } from './receita-federal.service';
export { default as nfseService } from './nfse.service';
export { default as esocialService } from './esocial.service';
export { default as sefazService } from './sefaz.service';
export { default as spedService } from './sped.service';
export { default as fgtsSimplesService } from './fgts-simples.service';
export { default as govbrEcacService } from './govbr-ecac.service';
export { default as syncCertificatesService } from './sync-certificates.service';
